import pandas as pd


def stockout_prevention(sku_results: dict, inventory_data: pd.DataFrame) -> dict:
    """
    Identify stockout risks and generate reorder recommendations for each SKU.

    Classifies SKUs based on Days of Supply (DOS), identifies high stockout
    probability, and generates reorder recommendations using the SKU's EOQ,
    supplier, and unit cost information.

    Risk thresholds:
        - DOS < 7: Critical
        - DOS < 14: Warning
        - DOS < 21: Medium
        - DOS >= 21: Normal
        - Stockout probability > 0.70: Reorder recommendation

    Args:
        sku_results: Dictionary containing KPI results for each SKU, including
            days of supply, stockout probability, and EOQ.
        inventory_data: DataFrame containing SKU details such as SKU name,
            supplier ID, and unit cost.

    Returns:
        A structured dictionary containing the engine name, triggered status,
        overall severity, SKU-level findings, and reorder recommendations.
    """

    results = {"engine_name": "stockout_prevention", "triggered": False, "severity": "normal", "findings": [], "recommendations": []}

    critical_count = warning_count = medium_count = 0

    for sku in sku_results:

        sku_details = inventory_data[inventory_data["sku_id"] == sku]

        if sku_results[sku]["dos"] < 7:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "days_of_supply": sku_results[sku]["dos"],
                                        "stockout_probability": sku_results[sku]["sop"],
                                        "risk_level": "critical"
            })
            critical_count += 1
        elif sku_results[sku]["dos"] < 14:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "days_of_supply": sku_results[sku]["dos"],
                                        "stockout_probability": sku_results[sku]["sop"],
                                        "risk_level": "high"
            })
            warning_count += 1
        elif sku_results[sku]["dos"] < 21:
            results["findings"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "days_of_supply": sku_results[sku]["dos"],
                                        "stockout_probability": sku_results[sku]["sop"],
                                        "risk_level": "medium"
            })
            medium_count += 1

        if sku_results[sku]["sop"] > 0.7 or sku_results[sku]["dos"] < 7:
            results["recommendations"].append({"sku_id": sku,
                                        "sku_name": sku_details["sku_name"].item(),
                                        "action": "reorder",
                                        "quantity": sku_results[sku]["eoq"],
                                        "supplier": sku_details["supplier_id"].item(),
                                        "estimated_cost": sku_results[sku]["eoq"] * sku_details["unit_cost"].item()
            })

    results["triggered"] = len(results["findings"]) > 0 or len(results["recommendations"]) > 0

    if critical_count > 0:
        results["severity"] = "critical"
    elif warning_count > 0:
        results["severity"] = "high"
    elif medium_count > 0:
        results["severity"] = "medium"
    else:
        results["severity"] = "normal"

    return results
