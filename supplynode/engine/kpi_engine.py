import math
from scipy.stats import poisson

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
