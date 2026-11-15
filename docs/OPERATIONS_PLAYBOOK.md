# OrderFlow operations playbook

## Daily order review

Begin with blocked and overdue open orders. Group by owner, priority, promised date, and reason code. Check the latest customer context, including existing cases, shipment activity, and any invoice records. Record the decision and next owner in the case workspace. If an order has no linked case, flag it for exception intake rather than assuming a resolution is underway.

## Blocked order analysis

**Inventory shortage:** confirm SKU, warehouse and requested quantity; review stock position and allocation options. A current stock snapshot alone cannot confirm the historic block reason.

**Credit hold:** coordinate with the appropriate financial owner and record the follow-up. Do not infer customer creditworthiness from order status.

**Incorrect pricing:** compare order price with the supported reference and request pricing review before reprocessing.

**Address validation or demand capture:** verify captured delivery details and customer instructions, then route corrections to the owning team.

## Delivery investigation

Review promised date, delivery date, ordered quantity, and delivered quantity. Separate lateness from short delivery: both affect OTIF, but typically involve different operational owners. Transportation-related issues may involve missed appointments or carrier delays; warehouse-related issues may involve picking and allocation.

## Billing investigation

Calculate the expected invoice amount using delivered quantity and order unit price, then compare it to the stored invoice value. Flag the result for review rather than automatically adjusting a financial record. In a production system, first reconcile tax, freight, discounts, debit/credit memos and negotiated pricing conditions.

## Root-cause review

Group exception cases by reason code and owner. Look for repeat patterns within the same warehouse, product category, and customer segment. A useful weekly review distinguishes immediate containment, a root-cause hypothesis, the accountable team, and a measurable corrective action.

## Operational controls

- Preserve an activity record when case state changes.
- Record a reason and a follow-up owner for unresolved exceptions.
- Review nearing-due cases before the agreed escalation threshold.
- Reconcile dashboard totals with the database after regenerating data.
- Treat all due dates and workflow thresholds in this repository as fictional operational assumptions.
