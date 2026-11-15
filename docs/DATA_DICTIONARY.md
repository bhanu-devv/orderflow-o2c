# Data dictionary and business relationships

Every field in this portfolio is synthetic. Foreign-key-like CSV fields correspond to SQLite constraints where applicable. Dates are ISO `YYYY-MM-DD`.

| Table | Key | Fields and meaning |
|---|---|---|
| customers | customer_id | customer_name, segment (Grocery/Distributor/etc.), region (East/Central/West) |
| products | sku | product_name, category, unit_price (fictional contracted line price) |
| orders | order_id | customer_id, sku, order_date, promised_date, ordered_qty, unit_price, order_amount, status, block_reason, priority, owner |
| shipments | delivery_id | order_id, delivery_date, delivered_qty, warehouse, carrier; each delivered order has one shipment |
| invoices | invoice_id | order_id, invoice_date, invoice_amount, payment_status; one invoice per delivered order |
| cases | case_id | order_id, reason_code, opened_date, sla_due_date, resolved_date, case_status, team, priority |
| inventory_snapshot | (sku,warehouse) | on_hand_qty, reorder_point; point-in-time only |
| activity_log | id | order_id, action, actor, note, changed_at; created when case actions occur in the Streamlit app |
| v_order_360 | order_id | joins customer/product/shipment/invoice and derives otif_flag and invoice_variance |

## Definition rules

- `order_amount = ordered_qty × unit_price`; generated amounts rounded to 2 decimals.
- `otif_flag = 1` only if status is Delivered, delivery date is at or before promised date, and delivered quantity is at least ordered quantity.
- OTIF denominator uses **delivered orders only**. Open, blocked and cancelled orders are excluded; this is the stated KPI convention for the simulation, not a universal industry definition.
- `invoice_variance = invoice_amount - delivered_qty × unit_price` for delivered orders.
- Some simulated invoices deliberately contain discrepancies; this is not an extraction error.
- Each delivered order has exactly one shipment and invoice, and each order holds one SKU. No multi-line or multi-shipment complexity is included.
- Case due dates are simplified day-level deadlines rather than precise timestamps. No claim of exact hours-based SLA compliance.
