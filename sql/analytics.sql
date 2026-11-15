-- SQLite order-to-cash reporting queries. Run against data/orderflow.db.
-- Delivered-only denominator; cancelled/open orders excluded from OTIF.
SELECT ROUND(100.0*SUM(otif_flag)/COUNT(*),2) AS otif_pct FROM v_order_360 WHERE status='Delivered';

-- Time-critical block queue: prioritizes critical, high, oldest promised date.
SELECT order_id,customer_name,promised_date,priority,block_reason,owner,order_amount
FROM v_order_360 WHERE status='Blocked'
ORDER BY CASE priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,promised_date;

-- Regional delivery performance.
SELECT region,COUNT(*) AS delivered_orders,SUM(otif_flag) AS otif_orders,
ROUND(100.0*SUM(otif_flag)/COUNT(*),2) AS otif_rate_pct
FROM v_order_360 WHERE status='Delivered' GROUP BY region ORDER BY otif_rate_pct;

-- Billing disputes: invoice difference from delivered quantity times unit price.
SELECT order_id,customer_name,delivered_qty,unit_price,invoice_amount,invoice_variance
FROM v_order_360 WHERE ABS(invoice_variance)>0.01 ORDER BY ABS(invoice_variance) DESC;

-- Unresolved SLAs relative to a fixed historical evaluation date for reproducibility.
SELECT reason_code,COUNT(*) unresolved, SUM(sla_due_date<'2026-11-14') overdue_as_of_snapshot
FROM cases WHERE case_status<>'Resolved' GROUP BY reason_code ORDER BY overdue_as_of_snapshot DESC;

-- Inventory below reorder threshold (snapshot only).
SELECT i.sku,p.product_name,i.warehouse,i.on_hand_qty,i.reorder_point,i.reorder_point-i.on_hand_qty AS reorder_gap
FROM inventory_snapshot i JOIN products p USING(sku) WHERE i.on_hand_qty<i.reorder_point ORDER BY reorder_gap DESC;
