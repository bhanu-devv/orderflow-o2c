# OrderFlow

## Order-to-Cash Operations & Customer Fulfillment Analytics

OrderFlow is an operations analytics project built around the day-to-day work of managing customer orders from placement through fulfillment and invoicing. It focuses on blocked-order visibility, on-time-in-full (OTIF) delivery, stock availability, service exceptions, billing mismatches, and customer communication.

The case study models a fictional consumer-goods distributor. **Every customer, order, shipment, and financial transaction is synthetic.** No proprietary employer or retail partner information is included.

### Project snapshot

| Indicator | Synthetic sample |
| --- | ---: |
| Customer orders | 10,000 |
| Delivered orders | 7,897 |
| Blocked orders | 805 |
| On time and in full | 5,378 |
| Delivered-order OTIF | 68.10% |
| Invoice discrepancies | 368 |
| Gross value of orders | $43,631,716.62 |

The intentionally imperfect dataset creates realistic investigation cases involving shortages, blocked orders, late deliveries, and reconciliation differences. The quoted OTIF measure uses delivered orders as its denominator, and therefore does not describe all orders due for delivery.

### What the system covers

- Daily order review and exception prioritization
- Customer-level view of orders, fulfillment, and invoicing
- Delivery performance and OTIF measurement
- Reason-coded customer cases, ownership, escalation, and audit trail
- Invoice-versus-delivery amount checks
- Warehouse inventory reorder alerts
- Data integrity controls and documented KPI definitions
- SQL reporting, spreadsheet-ready extracts, and BI model measures

### Architecture

```text
Customer master ─┐
                 ├── Sales orders ── Shipments
Product master ──┘          ├─────── Invoices
                            └─────── Cases ── Activity log
Product master ───────────────────── Inventory snapshot
```

SQLite is the local operational store; Python generates and validates the sample records; Streamlit provides the local workflow UI. Source files for Power BI calculations and Power Query modeling are kept separately.

### Run the project

Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/generate.py
streamlit run src/app.py
```

On Windows, activate the environment with `.venv\Scripts\activate`.

To run the automated data-integrity checks:

```bash
python -m unittest discover -s tests -v
```

To regenerate the offline report and Excel workbook, use the corresponding build scripts when available. Generated binary files are excluded from Git so the repository remains source-focused.

### Metric definitions

- **OTIF:** Delivered on or before the committed date and in full ordered quantity. For the sample scorecard, divide qualifying deliveries by delivered orders.
- **Invoice variance:** Invoice amount minus delivered quantity multiplied by unit price; differences above $0.01 require review.
- **Blocked backlog:** Orders currently in the Blocked state, grouped by blocking reason and urgency.
- **SLA exceptions:** Outstanding cases measured against an assigned service due date; day-level approximation.
- **Reorder alert:** Product stock on hand is below the defined reorder point in a current inventory snapshot.

### Scope and limitations

OrderFlow is a local analytical demonstration, not a live ERP or order management system. Each synthetic sales order has a single product line and, when delivered, one fulfillment and invoice record. Split shipments, credit notes, freight, taxes, and historical inventory movement accounting are out of scope. The application does not connect to SAP or Nestlé systems. Power BI DAX and Power Query files are development assets, not a native PBIX report.

The original full packaged demonstration also includes an offline HTML dashboard, a formula-based Excel tracker, and a seeded database. The repository contains reproducible source code and documentation.
