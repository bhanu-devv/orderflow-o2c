# Architecture and data flow

## Design objectives

OrderFlow separates source data, analytical joins, operational case updates, and presentation. The data generator gives each order a stable identifier and keeps referential relationships between customers, products, shipments, invoices, and cases. The same underlying records support the Streamlit workspace, offline dashboard, workbook, and SQL extracts.

## Data flow

1. `src/generate.py` produces reproducible tables and CSV extracts with a fixed random seed.
2. A normalized SQLite database stores the records, relationships, indices, and a joined `v_order_360` view.
3. `src/app.py` provides operational filters and case updates. Case changes write to SQLite and are recorded in `activity_log`.
4. `src/build_dashboard.py` reads source tables and exports a self-contained HTML report for offline distribution.
5. `src/build_excel.py` produces the standalone Excel operations tracker.
6. `sql/analytics.sql` provides reusable KPI queries; `powerbi/` contains semantic-model development assets.

```text
Synthetic order events
        │
        ▼
Python data generator ───────────────► CSV extracts
        │                                 │
        ▼                                 ├── Excel tracker
SQLite relational model                  └── Power BI source files
        │
        ├── v_order_360 ────────────────► HTML dashboard
        ├── SQL analytics
        └── Streamlit case workspace
                    │
                    ▼
            Case updates + audit log
```

## Storage and keys

`order_id`, `customer_id`, and `sku` are the principal identifiers. Shipments and invoices have unique `order_id` references. Case records may be many-to-one with orders. Inventory uses `(sku, warehouse)` as a composite key. An indexed order-status field supports queue filtering; case due dates are indexed for exception reviews.

## Mutable versus immutable data

The generated source tables represent a fixed historical sample. Only application case operations are intended to be mutable in day-to-day use. Regeneration resets all database tables and is therefore a destructive maintenance action. The offline dashboard and Excel tracker are generated artifacts: they do not automatically incorporate subsequent case status changes.

## Operational considerations

SQLite is suitable for local demonstration and single-user analysis. A multi-user deployment would require a transactionally managed database, authentication, scoped authorization, server-side validation, audit retention policy, backups, and concurrency testing. Customer and invoice data in this repository are fictional, so there is no access to confidential commercial records.

## SAP process mapping

The order-to-cash lifecycle is represented conceptually as sales order → availability and fulfillment checks → delivery → billing → customer issue resolution. The model does not execute SAP transactions or connect to SAP ECC or S/4HANA. Material availability, pricing conditions, credit management, and invoice posting are simplified for this project.
