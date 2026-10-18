# SupplyNode

**Inventory intelligence for small and medium-sized businesses.**

SupplyNode analyzes inventory, supplier, and sales records to identify stockout risks, slow-moving stock, and reorder needs. It combines deterministic KPI calculations and risk engines with a Claude-generated business summary, then saves the results for review.

This README describes the current `main` branch, including the PostgreSQL ingestion and persistence work merged during V2 development. It does not imply that all planned V2 features are complete. The `v1` branch preserves the completed V1 version.

## Current capabilities

- Read inventory, supplier, and sales data from PostgreSQL by default, or from an Excel workbook.
- Compute seven inventory KPIs per SKU.
- Detect stockout and dead-stock risks, and recommend reorder quantities, costs, and urgency.
- Coordinate the analysis through a sequential LangGraph workflow.
- Calculate a composite risk score and generate a concise Claude alert in Indian rupees.
- Print the alert, save a JSON report, and persist KPI snapshots and alerts in PostgreSQL with a shared run ID.
- Manage the database schema with Alembic and import the bundled sample workbook through a dedicated script.

## Workflow

```text
PostgreSQL (default) / Excel workbook
                  |
                  v
             KPI calculation
                  |
                  v
          Stockout prevention
                  |
                  v
          Dead-stock detection
                  |
                  v
          Reorder optimization
                  |
                  v
    Composite score + Claude summary
                  |
                  v
       Terminal alert + JSON file
                  |
                  v
 PostgreSQL KPI snapshots + alert record
```

Risk calculations and recommendations are rule-based. Claude summarizes the findings in **Situation / Root Cause / Action / Impact** format; it does not execute purchases or change stock levels.

## Setup

### Prerequisites

- Python 3.11, matching the included Dockerfile.
- A running PostgreSQL server with an application database and a separate test database, plus credentials with permission to create tables and read/write data.
- An Anthropic API key with access to the model configured in the orchestrator, currently `claude-sonnet-4-6`.

Run all commands below from the project root. Shell examples use Bash/Zsh syntax.

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

### 2. Configure environment variables

Create a `.env` file in the project root, replacing the example credentials:

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/supplynode
TEST_DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/supplynode_test
```

The current configuration requires **all three variables at import time**, including `TEST_DATABASE_URL` for normal application runs. Environment variables already set in the shell take precedence over `.env` values. Keep credentials out of version control; `.env` files are ignored.

Create the databases on your PostgreSQL server before applying migrations. Alembic creates the application tables, not the databases themselves.

### 3. Create the schema

```bash
python -m alembic upgrade head
```

This targets `DATABASE_URL` and creates the schema for suppliers, inventory, sales history, KPI snapshots, alerts, and overrides.

### 4. Import sample data

```bash
python scripts/migrate.py
```

This imports `supplynode/data/sample_data.xlsx` into PostgreSQL in supplier, inventory, then sales-history order. Existing primary keys are skipped, so rerunning the script does not update existing records. This is a data-import step, separate from Alembic schema migrations.

## Running SupplyNode

Read from PostgreSQL:

```bash
python main.py
```

Read from the bundled Excel workbook:

```bash
python main.py --excel
```

To use another workbook through the Python entry point:

```bash
python -c "from main import run_SupplyNode; run_SupplyNode('path/to/inventory.xlsx')"
```

**Excel mode still saves KPI snapshots and alerts to PostgreSQL.** It requires a migrated database with matching inventory SKU records because KPI snapshots reference the inventory table. Importing the bundled sample first satisfies this requirement for `--excel`; custom workbook SKUs must also exist in the database.

A full run sends engine findings to the Anthropic API and requires network access. Successful runs produce:

| Output | Contents |
| --- | --- |
| Terminal | Composite risk score and generated alert |
| `outputs/alerts/alert_YYYYMMDD_HHMMSS.json` | Timestamp, risk score, alert text, and all three engines' findings |
| `kpi_snapshots` table | Per-SKU KPI values linked to a UUID `run_id` |
| `alerts` table | The same run ID, highest engine severity, composite score, findings, alert text, and initial status `generated` |

The JSON report currently omits the run ID. JSON output, KPI snapshots, and the database alert are saved sequentially; they are not one atomic transaction.

## Input data

The workbook contains three sheets named exactly `inventory`, `suppliers`, and `sales_history`. Use [the sample workbook](supplynode/data/sample_data.xlsx) as the full template, especially for the import script, which reads additional business fields.

The analysis workflow uses these columns:

| Sheet | Analysis columns |
| --- | --- |
| `inventory` | `sku_id`, `sku_name`, `current_stock`, `opening_stock`, `avg_daily_demand`, `unit_cost`, `supplier_id`, `last_purchase_date` |
| `suppliers` | `supplier_id`, `supplier_name`, `avg_lead_time_days`, `reliability_score` |
| `sales_history` | `sku_id`, `date`, `quantity_sold`, `unit_price` |

For database imports, preserve the full sample schema, including product details, supplier contact fields, and transaction identifiers. See [the database models](db/models.py) and [the import script](scripts/migrate.py) for the complete field mapping.

Use unique SKU and supplier IDs, matching supplier references, parseable dates, positive daily demand and unit costs, and reliability scores between 0 and 1. Relevant inventory-value denominators must be nonzero. Each SKU needs sales history for the current persistence path: without it, the dead stock ratio is `None`, which the snapshot writer cannot convert to a float.

The Excel loader fills missing numeric values with zero and issues some warnings, but it does not fully validate inputs. The PostgreSQL loader reads all rows from the three source tables without filtering by date or active status.

## KPIs and risk rules

| KPI | Meaning |
| --- | --- |
| Days of supply | Current stock divided by average daily demand |
| Stockout probability | Poisson-based probability that demand exceeds stock during supplier lead time |
| Inventory turnover ratio | Sales-period cost of goods sold divided by average inventory value |
| Dead stock ratio | SKU value with no sale for at least 90 days, divided by total inventory value |
| Reorder point | Lead-time demand plus a 20% safety buffer |
| Carrying cost percentage | Annual carrying cost as a percentage of average inventory value |
| Economic order quantity | Order quantity calculated from annualized demand, ordering cost, and holding cost |

The composite score weights stockout severity at **50%**, dead-stock severity at **30%**, and reorder severity at **20%**. Severity values are `critical = 100`, `high = 70`, `medium = 40`, and `normal = 0`. This score is a severity indicator, not a probability.

Current rules and assumptions:

- Stockout severity is critical below 7 days of supply, high from 7 to under 14 days, and medium from 14 to under 21 days. Stockout probability above 70% also triggers a reorder recommendation.
- The dead-stock engine classifies turnover below 1 as critical, 1 to under 2 as high, and 2 to under 4 as medium.
- Reorder optimization handles critical and high stockout findings. It uses the SKU's assigned supplier and adds a safety buffer of `daily demand × lead time × (1 − reliability)` to EOQ, then rounds the quantity. A triggered reorder engine has critical severity.
- Annual carrying cost is fixed at 25%, and the EOQ order-cost assumption is Rs 500.
- EOQ annualizes all supplied sales quantities using `365 / 30`. Input sales should represent a 30-day period; the database loader does not enforce that window.
- Date-dependent calculations use the current date, so sample results change over time.

## Tests

The test suite covers loaders, KPI calculations, risk engines, CLI source selection, graph structure, JSON output, schema checks, sample-data imports, and repository persistence. It does not validate a live Claude response.

Database tests expect a migrated, sample-seeded test database with **3 suppliers, 5 inventory records, and 150 sales records**. Some loader tests use `DATABASE_URL` directly, while session-based tests use `TEST_DATABASE_URL`. Point both variables at the separate test database for the test session.

In a dedicated Bash/Zsh terminal, replace the example URL with your test database credentials, then run:

```bash
export TEST_DATABASE_URL='postgresql+psycopg2://user:password@localhost:5432/supplynode_test'
export DATABASE_URL="$TEST_DATABASE_URL"
python -m alembic upgrade head
python scripts/migrate.py
python -m pytest tests/ -v
```

Keep `ANTHROPIC_API_KEY` configured for imports. These shell overrides also affect application commands in that terminal; use your normal application environment when running against the application database.

## Project structure

```text
SupplyNode/
├── main.py                       # CLI and pipeline persistence
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Python 3.11 application image
├── alembic.ini
├── alembic/                      # Database schema migrations
├── db/
│   ├── models.py                 # SQLAlchemy models
│   └── repository.py             # KPI and alert persistence
├── scripts/migrate.py            # Sample Excel-to-PostgreSQL import
├── supplynode/
│   ├── data/                     # Excel/DB loaders and sample workbook
│   ├── engine/kpi_engine.py      # KPI calculations
│   ├── agents/                   # Risk engines and LangGraph orchestrator
│   └── utils/                    # Environment and database configuration
└── tests/                        # Unit and database integration tests
```

## Current scope

The implemented application is a manually invoked analysis pipeline. ERP connectors, direct CSV ingestion, a web dashboard, scheduled monitoring, WhatsApp delivery, automatic purchase execution, and adaptive learning are not part of the current workflow.

The `overrides` table provides schema groundwork; no override feedback loop is wired into the pipeline. Order fill rate and forecast accuracy have helper functions and nullable snapshot columns, but the pipeline does not compute them. Demand forecasting, seasonality adjustments, and dynamic supplier scoring remain outside the current implementation.
