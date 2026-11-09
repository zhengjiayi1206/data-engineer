-- 金额先汇总到订单粒度，避免明细扩行导致订单数重复。
WITH item_amount AS (
 SELECT order_id, SUM(price + freight_value) AS gmv
 FROM olist_order_items_dataset GROUP BY order_id
)
SELECT DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
 COUNT(*) AS total_orders,
 SUM(o.order_status = 'delivered') AS delivered_orders,
 SUM(o.order_status = 'canceled') AS canceled_orders,
 ROUND(100.0 * SUM(o.order_status = 'canceled') / NULLIF(COUNT(*), 0), 2) AS cancel_rate,
 ROUND(SUM(CASE WHEN o.order_status = 'delivered' THEN COALESCE(i.gmv, 0) ELSE 0 END), 2) AS delivered_gmv,
 ROUND(AVG(CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
 THEN TIMESTAMPDIFF(SECOND, o.order_purchase_timestamp, o.order_delivered_customer_date) / 86400.0 END), 2) AS avg_delivery_days
FROM olist_orders_dataset o LEFT JOIN item_amount i ON i.order_id = o.order_id
WHERE o.order_purchase_timestamp IS NOT NULL
GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') ORDER BY month;
