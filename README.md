# SAP P2P Analytics — Azure Data Factory, Snowflake & Power BI

**Status: locally executable proof of concept; cloud deployment not yet validated.**

A portfolio prototype of procure-to-pay analytics using wholly fictional SAP-shaped data. No SAP, Azure, Snowflake, or Power BI Service account is required to run the local pipeline.

## Architecture
Synthetic SAP-style extracts (EKKO, EKPO, LFA1, simplified invoice and goods receipt tables) → local landing → SQLite-based Silver cleaning/deduplication → Gold dimensional CSV exports → Power BI Desktop.

**Production target (deployment templates, not executed):** SAP extraction → Azure Data Factory → ADLS Gen2 → Snowpipe → Snowflake Bronze → Silver Dynamic Tables plus separate Streams/Tasks/MERGE example → Gold → Power BI.

## Run locally
Requires Python 3.11+; no external Python packages.

```bash
python src/generate.py
python src/run_pipeline.py
python -m unittest discover -s tests -v
```

The synthetic generator uses a fixed seed and creates 400 purchase orders, 12 revised header events, 20 suppliers, and sample invoices and receipts. Gold exports are generated in `data/gold/` for Power BI Desktop.

## Repository contents
- `src/` — synthetic data generation and local transformation pipeline
- `tests/` — purchase order uniqueness and invoice reference tests
- `snowflake/` — illustrative Bronze DDL, Silver Dynamic Table, Streams/Tasks/MERGE, minimal Gold
- `azure/adf/` — illustrative ADF Copy pipeline JSON; linked services and datasets are not included
- `powerbi/measures.dax` — sample executive KPI measures
- `.github/workflows/test.yml` — GitHub Actions CI for local tests

## Data grains and limitations
The demo uses one PO item per PO. `INVOICE` and `GOODS_RECEIPT` are simplified canonical extracts, **not** literal SAP RBKP/RSEG/EKBE schemas. Currency is EUR only.

This is **not** a live SAP connection, deployed ADF pipeline, running Snowflake environment, or completed Power BI PBIX. Snowflake SQL and ADF JSON require integration and deployment validation. Local SQLite does **not** emulate Snowflake Streams, Tasks, or Dynamic Tables.

## Next milestones
1. Add line-level invoices, credit notes, cancellations, and late-arriving CDC.
2. Add Bronze/Silver/Gold audit and reconciliation tests.
3. Complete deployable Azure/Snowflake ingestion and dimensional models.
4. Build a real Power BI Desktop PBIX and screenshots.
5. Add architecture diagrams, security documentation, and runbooks.

**Portfolio integrity:** No proprietary employer data or secrets are included.
