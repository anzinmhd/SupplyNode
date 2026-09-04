from supplynode.data import read_inventory_data
from supplynode.agents.orchestrator import app, save_alert

def run_SupplyNode(excel_path: str):
    print("")
    print("SupplyNode - Inventory Intelligence")
    print("=====================================")

    print("[1/5] Loading inventory data from Excel...")
    inventory_df, suppliers_df, sales_df = read_inventory_data(excel_path)
    print(f"      Loaded {len(inventory_df)} SKUs, {len(suppliers_df)} suppliers")

    print("[2/5] Computing KPIs...")
    print("[3/5] Running risk detection engines...")
    print("[4/5] Synthesizing with Claude AI...")

    result = app.invoke({
        "inventory_df": inventory_df,
        "suppliers_df": suppliers_df,
        "sales_df": sales_df,
        "kpi_results": {},
        "stockout_findings": {},
        "dead_stock_findings": {},
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

    save_alert(result)

if __name__ == "__main__":
    run_SupplyNode("supplynode/data/sample_data.xlsx")