-- 有原始类别但缺少英文翻译；原始类别为空另列为数据缺失，不混作翻译缺失。
SELECT p.product_category_name, COUNT(*) AS product_count
FROM olist_products_dataset AS p
LEFT JOIN product_category_name_translation AS t
  ON p.product_category_name = t.product_category_name
WHERE p.product_category_name IS NOT NULL
  AND (t.product_category_name IS NULL OR t.product_category_name_english IS NULL OR t.product_category_name_english = '')
GROUP BY p.product_category_name
ORDER BY product_count DESC, p.product_category_name;
