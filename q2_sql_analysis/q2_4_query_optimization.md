# Q2.4 慢查询分析与改写

原查询中订单商品和评价均可能一对多连接，形成行数乘积；同一商品金额被评价数重复放大，且评分被商品行数加权。`COUNT(DISTINCT)` 在放大结果上去重也有开销。`LOWER(city)` 对列求函数、`LIKE '%sao%'` 前置通配符，都无法有效使用普通 B-tree 范围检索。订单筛选和连接缺少合适索引时，将读取更多行。实际效果应以 MySQL 8 `EXPLAIN ANALYZE` 和真实数据分布验证。

以下明确每订单先求商品金额及评价均分，再以订单为单位统计；订单未评价不参与评分平均。此处收入沿用原题 price，不含运费。

```sql
WITH item AS (SELECT order_id, SUM(price) AS revenue FROM olist_order_items_dataset GROUP BY order_id),
review AS (SELECT order_id, AVG(review_score) AS score FROM olist_order_reviews_dataset GROUP BY order_id)
SELECT c.customer_state, COUNT(*) AS orders, SUM(COALESCE(i.revenue, 0)) AS revenue, AVG(r.score) AS avg_score
FROM olist_orders_dataset o JOIN olist_customers_dataset c ON c.customer_id=o.customer_id
LEFT JOIN item i ON i.order_id=o.order_id LEFT JOIN review r ON r.order_id=o.order_id
WHERE o.order_status='delivered' AND o.order_purchase_timestamp >= '2017-01-01'
  AND LOWER(c.customer_city) LIKE '%sao%'
GROUP BY c.customer_state ORDER BY revenue DESC;
```

可测试 `orders(order_status, order_purchase_timestamp, customer_id, order_id)`、商品和评价表的 `order_id`、客户表 `customer_id` 索引。先过滤符合条件的订单再聚合对应明细，可能更优，需比较执行计划；CTE 预聚合不保证总是更快。若业务只需城市精确匹配，可维护规范化城市并索引；任意子串需求则需评估全文检索或专门搜索方案，不能假装普通索引解决前置通配符。统一大小写、重音规则需与业务确认。

## 本机实测（原始规模，单次，非性能基准）

MySQL 8.4.13、当前 Olist 数据和已建连接索引下，原查询约 0.811 秒，改写约 1.080 秒；本次未得到性能提升，不能据此声称优化变快。两者订单数均为 20,367，但原查询商品金额合计 2,547,698.71，按订单预聚合后为 2,535,313.89，差额体现多对多连接导致的金额放大。两次未随机化运行顺序，也未排除缓存影响；100 倍数据上的耗时和索引效果需另行压测与 `EXPLAIN ANALYZE` 验证。
