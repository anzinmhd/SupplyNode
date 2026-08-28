import pandas as pd
from datetime import date

def deadstock_detection(sku_results: dict, inventory_data: pd.DataFrame) -> dict:
    """
    Detect dead stock and slow-moving inventory risks for each SKU.

    Classifies SKUs based on Inventory Turnover Ratio (ITR) and calculates
    the carrying cost being wasted on slow-moving or stagnant inventory.
    Generates markdown or return-to-supplier recommendations per flagged SKU.

    Risk thresholds:
        - ITR < 1  : Critical  — dead stock, capital fully locked
        - ITR 1-2  : High      — very slow moving, high carrying cost
        - ITR 2-4  : Medium    — slow moving, monitor and discount
        - ITR >= 4 : Normal    — healthy turnover, no action needed

    Args:
        sku_results: Dictionary containing KPI results for each SKU,
            including inventory turnover ratio and carrying cost percentage.
        inventory_data: DataFrame containing SKU details such as SKU name,
            current stock, unit cost, and last purchase date.

    Returns:
        A structured dictionary containing the engine name, triggered status,
        overall severity, SKU-level findings with carrying cost calculations,
        and markdown or return-to-supplier recommendations.
    """

    results = {"engine_name": "deadstock_detection", "triggered": False, "severity": "normal", "findings": [], "recommendations": []}
    
    dead_count = slow_moving_count = high_count = 0

    for sku in sku_results:
    
        sku_details = inventory_data[inventory_data["sku_id"] == sku]
        last_purchase = pd.to_datetime(sku_details["last_purchase_date"].item()).date()
        days_held = (date.today() - last_purchase).days

        if sku_results[sku]["itr"] < 1:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "inventory_turnover_ratio": sku_results[sku]["itr"],
                                        "carrying_cost_percentage": sku_results[sku]["ccp"],
                                        "carrying_cost": sku_details["current_stock"].item() * sku_details["unit_cost"].item() * (sku_results[sku]["ccp"] / 100) 
                                        * (days_held / 365),
                                        "risk_level": "critical"
            })

            results["recommendations"].append({"sku_id": sku,
                                                "sku_name": sku_details["sku_name"].item(),
                                                "action": "return to supplier or apply 20% markdown immediately"

            })
            dead_count +=1

        elif sku_results[sku]["itr"] < 2:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "inventory_turnover_ratio": sku_results[sku]["itr"],
                                        "carrying_cost_percentage": sku_results[sku]["ccp"],
                                        "carrying_cost": sku_details["current_stock"].item() * sku_details["unit_cost"].item() * (sku_results[sku]["ccp"] / 100) 
                                        * (days_held / 365),
                                        "risk_level": "high"
            }) 

            results["recommendations"].append({"sku_id": sku,
                                                "sku_name": sku_details["sku_name"].item(),
                                                "action": "apply 15% markdown within 7 days"

            })
            high_count += 1

        elif sku_results[sku]["itr"] < 4:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "inventory_turnover_ratio": sku_results[sku]["itr"],
                                        "carrying_cost_percentage": sku_results[sku]["ccp"],
                                        "carrying_cost": sku_details["current_stock"].item() * sku_details["unit_cost"].item() * (sku_results[sku]["ccp"] / 100) 
                                        * (days_held / 365),
                                        "risk_level": "medium"
            }) 

            results["recommendations"].append({"sku_id": sku,
                                                "sku_name": sku_details["sku_name"].item(),
                                                "action": "apply 10% markdown and monitor weekly"

            })
            slow_moving_count += 1


    results["triggered"] = len(results["findings"]) > 0

    if dead_count > 0:
        results["severity"] = "critical"
    elif high_count > 0:
        results["severity"] = "high"
    elif slow_moving_count > 0:
        results["severity"] = "medium"
    else:
        results["severity"] = "normal"

    return results
