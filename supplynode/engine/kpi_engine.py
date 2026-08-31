import math
import pandas as pd
from scipy.stats import poisson
from datetime import date, timedelta

# Days of supply
def compute_days_of_supply(stock: float, avg_daily_demand: float) -> float:
    if avg_daily_demand == 0:
        raise ValueError("Daily average demand cannot be zero")
    return stock / avg_daily_demand

# Stockout probability
def compute_stockout_probability(stock: float, avg_daily_demand: float, avg_lead_time: float) -> float:
    if avg_daily_demand == 0 or avg_lead_time == 0:
        return 0.0 # No demand or lead_time = no stockout risk
    demand_during_lead_time = avg_daily_demand * avg_lead_time
    return float(1 - poisson.cdf(stock, demand_during_lead_time))

# Inventory turnover ratio
def compute_inventory_turnover_ratio(cogs: float, avg_inventory: float) -> float:
    if avg_inventory == 0:
        raise ValueError("Average inventory cannot be zero")
    return cogs / avg_inventory

# Dead stock ratio
def compute_dead_stock_ratio(dead_stock_value: float, total_inventory_value: float) -> float:
    if total_inventory_value == 0:
        raise ValueError("Total inventory value cannot be zero")
    return dead_stock_value / total_inventory_value

# Re-order point
def compute_reorder_point(avg_daily_demand: float, avg_lead_time: float, safety_stock: float) -> float:
    lead_time_demand = avg_daily_demand * avg_lead_time
    return lead_time_demand + safety_stock

# Carrying cost percentage
def compute_carrying_cost_pct(annual_carrying_cost: float, avg_inventory_value: float) -> float:
    if avg_inventory_value == 0:
        raise ValueError("Average inventory value cannot be zero")
    return (annual_carrying_cost / avg_inventory_value) * 100

# Order fill rate
def compute_order_fill_rate_pct(order_fullfilled: float ,quantity_ordered: float) -> float:
    if quantity_ordered == 0:
        raise ValueError("Order quantity cannot be zero")
    return (order_fullfilled / quantity_ordered) * 100

# Demand forecast using mape
def compute_forecast_accuracy(actual: list, forecast: list) -> float:
    if len(actual) == 0 or len(forecast) == 0:
        raise ValueError("actual or forecast list cannot be empty")
    if len(actual) != len(forecast):
        raise ValueError("actual and forecast must be of same length")
    errors = [abs(a - f) / a for a,f in zip(actual, forecast )if a != 0]
    if len(errors) == 0:
        raise ValueError("actual list contains all zeros - cannot compute MAPE")
    return 100 - (sum(errors) / len(errors) * 100)

# Economic order quantity
def compute_eoq(annual_demand: float, order_cost: float, holding_cost: float) -> float:
    if holding_cost == 0:
        raise ValueError("Holding cost cannot be zero")
    return math.sqrt((2 * annual_demand * order_cost) / holding_cost)

# Compute all kpi for each sku and returns dict of dicts
def compute_all_kpi(inventory_data: pd.DataFrame, suppliers_data: pd.DataFrame, sales_history_data: pd.DataFrame) -> dict:
    """
    Computes all available V1 inventory KPIs for each SKU in the inventory DataFrame.

    Parameters:
        inventory_data (pd.DataFrame): Inventory sheet with stock levels, demand, and costs.
        suppliers_data (pd.DataFrame): Suppliers sheet with lead times and reliability scores.
        sales_history_data (pd.DataFrame): Sales history sheet with daily transaction records.

    Returns:
        dict: Nested dictionary of shape {sku_id: {kpi_name: value, ...}}
            Each SKU contains 7 computed KPIs based on available V1 data.

    KPIs computed per SKU:
        - days_of_supply         : Days of stock remaining at current demand rate
        - stockout_probability   : Probability of stockout during supplier lead time
        - inventory_turnover_ratio: How many times inventory cycles in the sales period
        - dead_stock_ratio       : Proportion of inventory that is slow-moving
        - reorder_point          : Stock level at which reorder should be triggered
        - carrying_cost_pct      : Annual carrying cost as a percentage of inventory value
        - eoq                    : Optimal order quantity to minimise total inventory cost

    Deferred to V2 (data not available in V1): 
        - order_fill_rate_pct    : Requires procurement/supply sheet
        - forecast_accuracy      : Requires demand forecast module
    """
    kpi_results = {}
    total_inventory_value = (inventory_data["current_stock"] * inventory_data["unit_cost"]).sum()
    threshold = 90 # For deadstock ratio

    for _, row in inventory_data.iterrows():
        sku = row["sku_id"]
        kpi_results[sku] = {}

        sku_avg_inventory_value = (
            (row["current_stock"] * row["unit_cost"]) + 
            (row["opening_stock"] * row["unit_cost"])
            ) /2
        sku_sales = sales_history_data[sales_history_data["sku_id"] == row["sku_id"]]

        supplier = suppliers_data[suppliers_data["supplier_id"] == row["supplier_id"]]
        avg_lead_time = supplier["avg_lead_time_days"].iloc[0]

        # Days of supply
        kpi_results[sku]["dos"] = compute_days_of_supply(row["current_stock"], row["avg_daily_demand"])

        # Stockout probability
        kpi_results[sku]["sop"] = compute_stockout_probability(row["current_stock"], row["avg_daily_demand"], avg_lead_time)

        # Inventory turnover ratio
        cogs = sales_history_data[sales_history_data["sku_id"] == row["sku_id"]]["quantity_sold"].sum() * row["unit_cost"]
        kpi_results[sku]["itr"] = compute_inventory_turnover_ratio(cogs, sku_avg_inventory_value)

        # Dead stock ratio
        if sku_sales.empty:
            kpi_results[sku]["dsr"] = None
        else:
            dead_stock_value = 0
            last_sale_date = pd.to_datetime(sku_sales["date"]).max().date()
            days_since_last_sale = (date.today() - last_sale_date).days
            if days_since_last_sale >= threshold:
                dead_stock_value = row["current_stock"] * row["unit_cost"]

            kpi_results[sku]["dsr"] = compute_dead_stock_ratio(dead_stock_value, total_inventory_value)

        # Reorder point
        safety_stock = .2 * row["avg_daily_demand"] * avg_lead_time
        kpi_results[sku]["rop"] = compute_reorder_point(row["avg_daily_demand"], avg_lead_time, safety_stock)

        # Carrying cost percentage
        carry_cost_rate = 0.25 # Hardcoded for v1
        kpi_results[sku]["ccp"] = compute_carrying_cost_pct(sku_avg_inventory_value * carry_cost_rate, sku_avg_inventory_value)

        # Order Fill Rate - will implement in V2

        # Demand forecast using mape - will implement in V2

        # Economic order quantity
        annual_demand = sku_sales["quantity_sold"].sum() * (365 / 30)
        order_cost = 500
        holding_cost = row["unit_cost"] * 0.25
        kpi_results[sku]["eoq"] = compute_eoq(annual_demand, order_cost, holding_cost)

    return kpi_results