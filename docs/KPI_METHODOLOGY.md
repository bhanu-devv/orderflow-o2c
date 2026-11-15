# KPI methodology

This document defines the measures used in the reports and their interpretation. Calculations use a reproducible synthetic order-to-cash dataset; they are not commercial performance claims.

## On-time-in-full (OTIF)

**Order-level OTIF:** A delivered order qualifies if `delivery_date <= promised_date` and `delivered_qty >= ordered_qty`.

**OTIF rate:** qualifying delivered orders divided by all delivered orders. The sample contains 5,378 qualifying orders among 7,897 delivered orders, giving **68.10%**.

Open, blocked, and cancelled orders are excluded from this denominator. This is an intentional choice for shipment performance analysis. A customer contract might instead measure deliveries due in a period, include missed/undelivered commitments, or use a line-item denominator. Those definitions produce different rates.

## Commercial value

**Gross ordered value:** sum of `ordered_qty × unit_price`, rounded to currency precision. Current generated total: **$43,631,716.62**.

This is an order pipeline amount, not invoices booked, shipments recognized as revenue, or cash collected. Order totals include cancelled and unfulfilled orders unless filtered explicitly.

## Order backlog

**Blocked backlog:** orders with `status = 'Blocked'`; 805 in the generated snapshot. The case queue is a separate exception-management object. A delivered order can also have an open case (for example, delivery or billing investigation), so the counts should not be equated.

## Invoice variance

For delivered orders, `invoice_variance = invoice_amount − delivered_qty × order_unit_price`.

A record is flagged when absolute variance exceeds $0.01. The generated dataset contains **368** such cases. The model does not include taxes, freight, promotions, deductions, multi-currency conversions, or credit memos; a real billing process would reconcile those separately before classifying an invoice as erroneous.

## Inventory alerts

The inventory file represents a single snapshot per `(sku, warehouse)`. An alert occurs when `on_hand_qty < reorder_point`. It is a replenishment review signal, not proof that a historical order was blocked for stock reasons. No daily receipts, allocations, demand forecasts, or transfer orders are modeled.

## SLA and priority

Case due dates are represented as calendar dates rather than time-zone-aware timestamps. High/Critical priority, unresolved status, approaching due date, and reason code can be used to prioritize the queue. The sample should not be used to claim compliance with a real SLA measured in business hours.

## Reconciliation

`data/validation.json` contains expected totals. `tests/test_integrity.py` validates join integrity and benchmark counts. Analytical queries in `sql/analytics.sql` can be run against `data/orderflow.db` to independently reproduce key results. Dashboard figures should be checked against the database after regenerating or changing the data.
