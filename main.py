import uuid
import argparse

from supplynode.data import read_inventory_data, read_inventory_data_db
from supplynode.agents.orchestrator import app, save_alert_json

from db.repository import save_kpi_snapshots, save_alert_db

def run_SupplyNode(excel_path: str | None = None):
    run_id = str(uuid.uuid4())
    print("")
    print("SupplyNode - Inventory Intelligence")
    print("=====================================")

    if excel_path is None:
        print("[1/5] Loading inventory data from PostgreSQL...")
        inventory_df, suppliers_df, sales_df = read_inventory_data_db()
    else:
        print("[1/5] Loading inventory data from Excel...")
        inventory_df, suppliers_df, sales_df = read_inventory_data(excel_path)

    print(f"      Loaded {len(inventory_df)} SKUs, {len(suppliers_df)} suppliers")

    print("[2/5] Computing KPIs...")
    print("[3/5] Running risk detection engines...")
    print("[4/5] Synthesizing with Claude AI...")

    result = app.invoke({
        "run_id": run_id,
        "inventory_df": inventory_df,
        "suppliers_df": suppliers_df,
        "sales_df": sales_df,
        "kpi_results": {},
        "stockout_findings": {},
        "deadstock_findings": {},
        "reorder_findings": {},
        "composite_risk_score": 0.0,
        "final_alert": "",
        "alert_metadata": {}        
    })

    print("[5/5] Alert generated")
    print("")
    print("=" * 50)
    print("SUPPLYNODE ALERT")
    print("=" * 50)
    print(f"Risk Score: {result['composite_risk_score']}/100")
    print("")
    print(result['final_alert'])
    print("=" * 50)
    print("")

    save_alert_json(result)

    findings = {
        "stockout": result["stockout_findings"],
        "deadstock": result["deadstock_findings"],
        "reorder": result["reorder_findings"],
    }

    severity = max(
        result["stockout_findings"]["severity"],
        result["deadstock_findings"]["severity"],
        result["reorder_findings"]["severity"],
        key=lambda x: {
            "normal": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }[x],
    )

    save_kpi_snapshots(
        run_id=run_id,
        kpi_results=result["kpi_results"],
    )

    save_alert_db(
        run_id=run_id,
        severity=severity,
        composite_risk_score=result["composite_risk_score"],
        findings=findings,
        alert_message=result["final_alert"],
    )


def main():
    # Parse command-line arguments to select the data source
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--excel",
        action="store_true",     # Use Excel instead of PostgreSQL
    )
    
    args = parser.parse_args()

    if args.excel:
        run_SupplyNode("supplynode/data/sample_data.xlsx")
    else:
        run_SupplyNode()
    
if __name__ == "__main__":
    main()