import pandas as pd

def reorder_optimization(stockout_results: dict, kpi_results: dict, inventory_data: pd.DataFrame, supplier_data: pd.DataFrame) -> dict:
    """
    Generate optimized reorder recommendations for SKUs flagged by the Stockout Prevention Engine.

    Runs only on SKUs classified as critical or high risk by the stockout engine.
    Computes the optimal reorder quantity by combining EOQ with a safety stock buffer
    based on supplier reliability. Selects the best available supplier and estimates
    the total reorder cost in Indian Rupees.

    Reorder quantity formula:
        safety_stock = avg_daily_demand x avg_lead_time x (1 - reliability_score)
        reorder_quantity = round(EOQ + safety_stock)

    Urgency classification:
        - DOS < 7  : immediate  — order today
        - DOS < 14 : this_week  — order within 7 days
        - DOS >= 14: plan_ahead — schedule reorder

    Args:
        stockout_results: Output dictionary from stockout_prevention engine.
            Used to identify which SKUs require reorder (critical or high risk_level only).
        kpi_results: Dictionary containing pre-computed KPI results per SKU,
            including EOQ, days of supply, and reorder point.
        inventory_data: DataFrame containing SKU details such as SKU name,
            unit cost, avg daily demand, and supplier ID.
        supplier_data: DataFrame containing supplier details such as supplier name,
            avg lead time, and reliability score.

    Returns:
        A structured dictionary containing the engine name, triggered status,
        overall severity, findings with full reorder details per SKU,
        and recommendations list.
    """

    results = {"engine_name": "reorder_optimization", "triggered": False, "severity": "normal", "findings": [], "recommendations": []}

    for finding in stockout_results["findings"]:
        
        sku_details = inventory_data[inventory_data["sku_id"] == finding["sku_id"]]
        supplier_details = supplier_data[supplier_data["supplier_id"] == sku_details["supplier_id"].item()]

        if finding["risk_level"] == "critical" or finding["risk_level"] == "high":
            eoq = kpi_results[finding["sku_id"]]["eoq"]
            safety_stock = sku_details["avg_daily_demand"].item() * supplier_details["avg_lead_time_days"].item() * (1 - supplier_details["reliability_score"].item())

            if kpi_results[finding["sku_id"]]["dos"] < 7:
                urgency = "immediate"
            elif kpi_results[finding["sku_id"]]["dos"] < 14:
                urgency = "this_week"
            else:
                urgency = "plan_ahead"
            
            results["findings"].append({
            "sku_id": finding["sku_id"],
            "sku_name": sku_details["sku_name"].item(),
            "reorder_quantity": round(eoq + safety_stock),
            "safety_stock": safety_stock,                 
            "best_supplier_id": supplier_details["supplier_id"].item(),
            "best_supplier_name": supplier_details["supplier_name"].item(),
            "supplier_reliability": supplier_details["reliability_score"].item(),
            "estimated_cost": round(eoq + safety_stock) * sku_details["unit_cost"].item(),
            "urgency": urgency,
            "days_until_stockout": kpi_results[finding["sku_id"]]["dos"],
            "reorder_point": kpi_results[finding["sku_id"]]["rop"]            
            })

    results["triggered"] = len(results["findings"]) > 0 or len(results["recommendations"]) > 0

    if results["triggered"]:
        results["severity"] = "critical"

    return results


