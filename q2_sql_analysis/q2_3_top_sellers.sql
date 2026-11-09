-- 销售额按明细所属卖家归属；订单、评价和延迟按卖家-订单去重。
WITH seller_order AS (
 SELECT seller_id, order_id, SUM(price + freight_value) AS gmv
 FROM olist_order_items_dataset GROUP BY seller_id, order_id
), order_review AS (
 SELECT order_id, AVG(review_score) AS order_score FROM olist_order_reviews_dataset GROUP BY order_id
), seller_metrics AS (
 SELECT so.seller_id, s.seller_state, SUM(so.gmv) AS gmv_2017,
 COUNT(*) AS order_count, COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
 AVG(r.order_score) AS avg_review_score,
 100.0 * SUM(CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL AND o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END)
 / NULLIF(SUM(CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL THEN 1 ELSE 0 END),0) AS late_delivery_rate,
 100.0 * SUM(o.order_status = 'canceled') / NULLIF(COUNT(*), 0) AS cancel_rate
 FROM seller_order so JOIN olist_orders_dataset o ON o.order_id=so.order_id
 JOIN olist_sellers_dataset s ON s.seller_id=so.seller_id
 LEFT JOIN olist_customers_dataset c ON c.customer_id=o.customer_id
 LEFT JOIN order_review r ON r.order_id=o.order_id
 WHERE o.order_purchase_timestamp >= '2017-01-01' AND o.order_purchase_timestamp < '2018-01-01'
 GROUP BY so.seller_id,s.seller_state
), ranked AS (
 SELECT seller_metrics.*, RANK() OVER (PARTITION BY seller_state ORDER BY gmv_2017 DESC) AS state_rank
 FROM seller_metrics
)
SELECT seller_id,seller_state,ROUND(gmv_2017,2) AS gmv_2017,order_count,unique_customers,
 ROUND(avg_review_score,2) AS avg_review_score,ROUND(late_delivery_rate,2) AS late_delivery_rate,
 ROUND(cancel_rate,2) AS cancel_rate,state_rank
FROM ranked ORDER BY gmv_2017 DESC,seller_id LIMIT 20;
