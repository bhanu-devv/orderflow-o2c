# OrderFlow

### Order-to-cash operations and customer fulfillment analytics

OrderFlow brings sales orders, deliveries, customer cases, inventory snapshots, and invoices into one operational view. It combines a local order-management workspace, an offline reporting dashboard, Excel tracking, and SQL analysis to support the questions that come up in a typical order-to-cash review: Which orders need attention? Where are deliveries falling short? Which exceptions are approaching their due dates? Which invoices do not match fulfilled quantities?

The dataset represents a fictional consumer-goods distributor. All customer names, products, orders, prices, delivery events, and cases are synthetic. OrderFlow is an independent project and is not affiliated with a commercial brand, retailer, or staffing company.

## Overview

| Area | Implementation |
| --- | --- |
| Order management | Searchable order queue with status, owner, priority, and customer filters |
| Customer visibility | Combined order, shipment, invoice, and exception history |
| Delivery performance | On-time-in-full (OTIF) measures and service trends |
| Exception handling | Case ownership, reason codes, due dates, status updates, and local activity log |
| Inventory | Warehouse-level available-stock snapshot and reorder-point alerts |
| Billing | Comparison of invoice amount against delivered quantity at order price |
| Reporting | Interactive Streamlit workspace, self-contained HTML dashboard, Excel operations workbook |
| Data | Reproducible Python generator, CSV extracts, relational SQLite database, SQL reporting queries |
| BI development | DAX measure definitions and Power Query transformation template |

## Operational snapshot

The sample dataset is generated with fixed seed `20261114`. CSV extracts are committed, while the SQLite database is recreated on a local machine by running `python src/generate.py`.

| Measure | Result | Basis |
| --- | ---: | --- |
| Orders | 10,000 | One order record per SKU |
| Delivered | 7,897 | Orders marked Delivered with a shipment record |
| Blocked | 805 | Orders currently in Blocked status |
| On time and in full | 5,378 | Delivered by the promised date in the full ordered quantity |
| OTIF | 68.10% | 5,378 / 7,897 delivered orders |
| Invoice exceptions | 368 | Invoice value differs from delivered quantity × unit price by more than $0.01 |
| Total order value | $43,631,716.62 | Gross ordered quantity × unit price; not booked revenue or collected cash |

OTIF is intentionally calculated over *delivered orders* for this analysis. Undelivered orders are reported in backlog measures rather than assigned an OTIF result. See [KPI methodology](docs/KPI_METHODOLOGY.md) for definitions, trade-offs, and data limitations.

## Application

### Streamlit workspace

`src/app.py` provides a locally hosted operations application with six working areas:

1. **Executive overview** — headline metrics, exception categories, delivery performance, and order value.
2. **Order filter** — prioritized daily work queue and customer/order lookup.
3. **Exception cases** — status and ownership tracking with notes and an activity log in SQLite.
4. **Customer 360** — order-to-delivery-to-invoice visibility for a selected customer.
5. **Billing reconciliation** — investigate billed value relative to delivered quantities.
6. **Inventory and quality** — reorder alerts and referential-integrity checks.

Case status updates are saved to the local SQLite file. The bundled dataset can be restored by running the generator; running it replaces the original case records and clears any local activity history.

### Standalone dashboard

[`dashboard/OrderFlow_Offline_Dashboard.html`](dashboard/OrderFlow_Offline_Dashboard.html) is a self-contained report. It is useful for reviewing the data without a Python environment or network connection. The dashboard supports operational filtering, customer and region comparisons, and individual order inspection. It is generated from the data by `src/build_dashboard.py`.

### Excel workbook

[`excel/OrderFlow_Operations_Tracker.xlsx`](excel/OrderFlow_Operations_Tracker.xlsx) contains an operations scorecard and a filtered sample of 250 orders, including calculated fields, priority indicators, and reconciliation formulas. The full 10,000-order extract is also available in `data/orders.csv`. The workbook is a formula-driven tracker; it does not contain a preconfigured PivotTable.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── shipments.csv
│   ├── invoices.csv
│   ├── cases.csv
│   ├── inventory_snapshot.csv
│   ├── orderflow.db  # generated locally, not committed
│   └── validation.json
├── src/
│   ├── app.py
│   ├── generate.py
│   ├── build_dashboard.py
│   └── build_excel.py
├── dashboard/
│   └── OrderFlow_Offline_Dashboard.html
├── excel/
│   └── OrderFlow_Operations_Tracker.xlsx
├── sql/
│   └── analytics.sql
├── powerbi/
│   ├── Measures.dax
│   └── PowerQuery_Orders.m
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── KPI_METHODOLOGY.md
│   └── OPERATIONS_PLAYBOOK.md
└── tests/
    └── test_integrity.py
```

## Run locally

Requirements: Python 3.10+ and a modern web browser. SQLite is included with Python. The prebuilt HTML report and Excel file can be opened without installing Python dependencies.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/generate.py
streamlit run src/app.py
```

```powershell
# Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/generate.py
streamlit run src/app.py
```

The application reads `data/orderflow.db`, generated locally by `python src/generate.py` (the database file is deliberately not committed), and writes changes to its case records and audit log. A backup of that file is recommended if you want to preserve a particular investigation state.

### Rebuild data and reporting outputs

```bash
python src/generate.py
python src/build_dashboard.py
python -m unittest discover -s tests -v
```

`src/build_excel.py` rebuilds the Excel file and requires `artifact_tool`, which is not listed in the runtime requirements. The included workbook opens without this package.

## Analytical model

The model follows a compact sales-order star with separate fulfillment and finance events:

```text
customers ─┐
           ├── orders ── shipments
products ──┘       ├──── invoices
                   └──── cases ── activity_log
products ─────────────── inventory_snapshot
```

- Customer and product are master records.
- Each order represents a single product line and one ordered quantity.
- A delivered order has one delivery note and one invoice in the current model.
- Cases track exceptions independently of shipment/invoice status.
- Inventory is a current warehouse snapshot, not a historical stock movement ledger.
- `v_order_360` is a SQLite view joining the main commercial and fulfillment entities.

Foreign keys and indices are defined in the generator; the [data dictionary](docs/DATA_DICTIONARY.md) documents fields and derived measures. The [architecture notes](docs/ARCHITECTURE.md) explain design choices and boundaries.

## Power BI assets

The `powerbi/` folder contains DAX measure definitions and an example Power Query transformation for the order extract. They are source files for a Power BI semantic model, **not** a completed `.pbix` report.

Recommended report pages are Executive Performance, OTIF and Transportation, Blocked Order Queue, Customer 360, and Billing Exceptions. Relationships should follow the SQL data model, with active joins between orders and shipments/invoices. The DAX files should be validated against `data/validation.json` after model relationships and field types are configured.

## SQL analysis

[`sql/analytics.sql`](sql/analytics.sql) includes queries covering order status, blocked-order backlog, OTIF, customer-level fulfillment, invoice mismatches, and aged exceptions. Queries run against `data/orderflow.db` using SQLite-compatible SQL.

## Quality checks

```bash
python -m unittest discover -s tests -v
```

The integrity suite covers expected record volumes, foreign-key validity, order-to-shipment coverage, invoice coverage, positive commercial amounts, expected OTIF results, and case referential integrity. Seven tests are included. Counts and reporting metrics from the generation step are stored in `data/validation.json` for reconciliation.

## Design boundaries

- The system uses synthetic data exclusively; the metrics do not represent an operating company.
- SLA deadlines are day-level approximations, not a timestamp-based production SLA engine.
- Inventory alerts use a point-in-time snapshot and cannot establish historic stock availability.
- Each order has one line and, where delivered, one shipment and one invoice; there are no split deliveries, credits, freight allocations, or tax components.
- OTIF measures are based on a documented denominator, which may differ from contractual customer scorecards.
- SAP-style order-to-cash terminology informs the data model, but there is no SAP connection.
- The included Power BI files are development assets; the finished reports are the HTML dashboard and Excel workbook.

## Technical stack

Python, pandas, Streamlit, SQLite, Excel, JavaScript/HTML, SQL, DAX, and Power Query (M).
