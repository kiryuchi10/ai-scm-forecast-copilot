-- =========================================
-- 03_verify.sql
-- 목적: CSV 적재 후 테이블 행 수 및 샘플 데이터 확인
-- 사용: mysql -u scmcore -p scmcore < db/03_verify.sql
-- =========================================

USE scmcore;

SELECT '=== 테이블별 행 수 ===' AS '';
SELECT 'dim_category'    AS tbl, COUNT(*) AS cnt FROM dim_category
UNION ALL SELECT 'dim_department', COUNT(*) FROM dim_department
UNION ALL SELECT 'dim_product',     COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_customer',    COUNT(*) FROM dim_customer
UNION ALL SELECT 'fact_order',      COUNT(*) FROM fact_order
UNION ALL SELECT 'fact_order_item', COUNT(*) FROM fact_order_item
UNION ALL SELECT 'fact_shipping',   COUNT(*) FROM fact_shipping;

SELECT '=== dim_product 샘플 5건 ===' AS '';
SELECT id, product_key, product_name, category_id, department_id, base_price FROM dim_product LIMIT 5;

SELECT '=== fact_order_item 샘플 5건 ===' AS '';
SELECT oi.id, oi.order_item_key, oi.order_id, oi.product_id, oi.quantity, oi.sales
FROM fact_order_item oi LIMIT 5;

SELECT '=== 일별 주문 수 (최근 5일) ===' AS '';
SELECT DATE(order_date) AS dt, COUNT(*) AS orders
FROM fact_order
GROUP BY DATE(order_date)
ORDER BY dt DESC
LIMIT 5;
