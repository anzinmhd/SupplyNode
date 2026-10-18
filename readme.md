# SupplyNode — V1

**Inventory intelligence for small and medium-sized businesses.**

SupplyNode reads inventory, supplier, and sales data from an Excel workbook, computes inventory KPIs, and identifies stockout, dead-stock, and reorder risks. A LangGraph workflow combines deterministic analysis with a Claude-generated summary to produce an actionable alert in the terminal and a saved JSON report.

This README documents the implementation on the `v1` branch.

## V1 capabilities

- Load inventory records from a three-sheet Excel workbook.
- Compute seven KPIs per SKU: days of supply, stockout probability, inventory turnover ratio, dead stock ratio, reorder point, carrying cost percentage, and economic order quantity (EOQ).
- Detect stockout risks and slow-moving inventory using rule-based engines.
- Recommend reorder quantities with a supplier-reliability safety buffer, estimated costs, and urgency.
- Calculate a composite risk score from 0 to 100.
- Generate a plain-language alert using Claude, structured as **Situation / Root Cause / Action / Impact**.
- Save engine findings, the risk score, and the generated alert as timestamped JSON.

## Workflow

```text
Excel workbook: inventory / suppliers / sales_history
                         |
                         v
                    KPI engine
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
          Composite risk score + Claude summary
                         |
                         v
              Terminal alert + JSON report
```

LangGraph runs these stages sequentially. KPI calculations and risk classifications are deterministic; Claude turns the findings into a business-facing summary.

## Getting started

Use Python 3.11 to match the supplied Docker image. Run the following commands from the project root.

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with `.venv\Scripts\Activate.ps1`.

### 2. Configure the API key

Create a `.env` file in the project root containing:

```dotenv
ANTHROPIC_API_KEY=your_anthropic_api_key
```

You can also provide `ANTHROPIC_API_KEY` as an environment variable. The orchestrator requires this value when imported. A full run sends engine findings to the Anthropic API and requires network access and API access to the configured model, `claude-sonnet-4-6`.

### 3. Run the sample

```bash
python main.py
```

The entry point loads `supplynode/data/sample_data.xlsx`, prints the risk score and alert, and saves a report to:

```text
outputs/alerts/alert_YYYYMMDD_HHMMSS.json
```

The report contains `timestamp`, `risk_score`, `final_alert`, `stockout_findings`, `deadstock_findings`, and `reorder_findings`.

To analyze another workbook without changing the entry point:

```bash
python -c "from main import run_SupplyNode; run_SupplyNode('path/to/inventory.xlsx')"
```

## Excel input format

Use the included sample workbook as a template. Sheet names and column names must match exactly.

| Sheet | Required columns for the V1 workflow |
| --- | --- |
| `inventory` | `sku_id`, `sku_name`, `current_stock`, `opening_stock`, `avg_daily_demand`, `unit_cost`, `supplier_id`, `last_purchase_date` |
| `suppliers` | `supplier_id`, `supplier_name`, `avg_lead_time_days`, `reliability_score` |
| `sales_history` | `sku_id`, `date`, `quantity_sold`, `unit_price` |

Provide one inventory row per SKU and one supplier row per supplier ID. Every inventory supplier ID must match a supplier row. Use parseable dates, positive daily demand and unit costs, and supplier reliability scores between 0 and 1. Average inventory value and total inventory value must be nonzero for the relevant KPI calculations.

The loader fills missing numeric values with zero and warns about some missing identifiers or zero values; it does not perform complete input validation. A warning does not guarantee that downstream calculations can proceed.

## Risk scoring and assumptions

The composite score weights engine severities as follows:

| Engine | Weight |
| --- | --- |
| Stockout prevention | 50% |
| Dead-stock detection | 30% |
| Reorder optimization | 20% |

Severity values are `critical = 100`, `high = 70`, `medium = 40`, and `normal = 0`. The score is a weighted severity indicator, not a probability.

V1 uses these fixed assumptions:

- Stockout severity is critical below 7 days of supply, high from 7 to under 14 days, and medium from 14 to under 21 days. Reorder recommendations also consider stockout probability above 70%.
- Dead-stock engine severity uses inventory turnover: below 1 is critical, 1 to under 2 is high, and 2 to under 4 is medium. The separate dead stock ratio KPI uses a 90-day period since the last sale.
- Annual carrying cost is 25% of inventory value; the EOQ order-cost assumption is Rs 500.
- EOQ annualizes sales quantities using `365 / 30`, so the sales input should represent a 30-day period.
- The reorder point uses a buffer of 20% of lead-time demand. Reorder optimization separately uses `daily demand × lead time × (1 − supplier reliability)` as its safety buffer.
- Reorder optimization processes critical and high stockout findings and uses the SKU's assigned supplier. Any resulting reorder findings give that engine a critical severity.
- Date-dependent calculations use the current date, so results from the sample workbook change over time.

## Tests

With dependencies installed and `ANTHROPIC_API_KEY` set, run:

```bash
python -m pytest tests/ -v
```

The existing tests cover data loading, KPI calculations, risk engines, composite scoring, JSON persistence, and graph structure. They do not invoke Claude to validate a live generated alert.

## Project structure

```text
SupplyNode/
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Python 3.11 container
├── supplynode/
│   ├── data/
│   │   ├── loader.py              # Excel ingestion
│   │   └── sample_data.xlsx       # Example input workbook
│   ├── engine/kpi_engine.py       # Inventory KPI calculations
│   ├── agents/
│   │   ├── stockout_engine.py
│   │   ├── deadstock_engine.py
│   │   ├── reorder_engine.py
│   │   └── orchestrator.py        # LangGraph workflow and Claude alert
│   └── utils/config.py            # API key configuration
└── tests/                         # Automated tests
```

## Scope and limitations

V1 is a manually run Excel-to-alert workflow. ERP integrations such as Zoho, Tally, Odoo, and ERPNext, direct CSV ingestion, WhatsApp delivery, continuous monitoring, and adaptive feedback loops are outside this version's implemented workflow. It produces recommendations; it does not place purchase orders or update inventory records.

Order fill rate and forecast accuracy have standalone helper functions but are not included in the seven-KPI pipeline. Demand forecasting, seasonality adjustments, and dynamic supplier scoring are not implemented in V1.
