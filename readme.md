# SupplyNode

Inventory intelligence for SMEs. SupplyNode reads PostgreSQL or Excel data,
computes inventory KPIs, detects stockout and dead-stock risks, and recommends
reorder quantities. Claude turns the engine findings into a plain-language alert.

The current implementation is a CLI that performs one analysis per invocation.
It prints the alert, exports JSON, and stores KPI snapshots and alerts in
PostgreSQL. It does not continuously monitor inventory or place orders.

## Architecture

```text
PostgreSQL or Excel workbook
             |
             v
       Data ingestion
             |
             v
    LangGraph workflow
    KPI computation
       -> Stockout detection
       -> Dead-stock detection
       -> Reorder optimization
       -> Weighted risk score + Claude alert
             |
             v
Terminal + JSON export + PostgreSQL persistence
```

Risk detection and scoring use deterministic rules. Claude generates the alert
text using `claude-sonnet-4-6`; engine findings are sent to the Anthropic API.
The score weights stockout severity at 50%, dead-stock severity at 30%, and
reorder severity at 20%.

ERP connectors (Zoho, Tally, Odoo, ERPNext), CSV ingestion, WhatsApp delivery,
scheduled monitoring, and adaptive feedback, seasonality, and supplier-scoring
loops are planned capabilities, not implemented features. There is no web UI in
this version.
