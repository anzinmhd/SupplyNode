import pytest
import pandas as pd
from supplynode.engine import (
    compute_days_of_supply,
    compute_stockout_probability,
    compute_inventory_turnover_ratio,
    compute_dead_stock_ratio,
    compute_reorder_point,
    compute_carrying_cost_pct,
    compute_order_fill_rate_pct,
    compute_forecast_accuracy,
    compute_eoq,
    compute_all_kpi
)

def test_compute_days_of_supply():
    assert compute_days_of_supply(100, 10) == 10

def test_compute_days_of_supply_zero_demand():
    with pytest.raises(ValueError):
        compute_days_of_supply(100, 0)

def test_compute_stockout_probability():
    assert compute_stockout_probability(50, 7, 7) == pytest.approx(0.4063, abs=1e-4)

def test_compute_stockout_probability_zero_avg_demand_or_zero_avg_lead_time():
    assert compute_stockout_probability(100, 0, 7) == 0.0
    assert compute_stockout_probability(100, 10, 0) == 0.0

def test_compute_inventory_turnover_ratio():
    assert compute_inventory_turnover_ratio(100, 25) == 4

def test_compute_inventory_turnover_ratio_zero_avg_inventory():
    with pytest.raises(ValueError):
        compute_inventory_turnover_ratio(100, 0)

def test_compute_dead_stock_ratio():
    assert compute_dead_stock_ratio(100, 200) == 0.5

def test_compute_dead_stock_ratio_zero_inventory_value():
    with pytest.raises(ValueError):
        compute_dead_stock_ratio(100, 0)

def test_compute_reorder_point():
    assert compute_reorder_point(10, 7, 10) == 80
    assert compute_reorder_point(20, 5, 15) == 115

def test_compute_carrying_cost_pct():
    assert compute_carrying_cost_pct(100, 500) == 20

def test_compute_carrying_cost_pct_zero_avg_inventory_value():
    with pytest.raises(ValueError):
        compute_carrying_cost_pct(100, 0)

def test_compute_order_fill_rate_pct():
    assert compute_order_fill_rate_pct(80, 100) == 80

def test_compute_order_fill_rate_pct_zero_ordered_qty():
    with pytest.raises(ValueError):
        compute_order_fill_rate_pct(80, 0)

def test_compute_forecast_accuracy():
    assert compute_forecast_accuracy([20, 29, 37, 40], [25, 27, 37, 41]) == pytest.approx(91.40, abs=0.01)

def test_compute_forecast_accuracy_len_zero():
    with pytest.raises(ValueError):
        compute_forecast_accuracy([], [])

def test_compute_forecast_accuracy_len_lists_not_equal():
    with pytest.raises(ValueError):
        compute_forecast_accuracy([20, 29, 37, 40], [25, 27, 37,])

def test_compute_forecast_accuracy_all_zeros():
    with pytest.raises(ValueError):
        compute_forecast_accuracy([0, 0, 0], [10, 20, 30])

def test_compute_eoq():
    assert compute_eoq(2000, 500, 20) == pytest.approx(316.23, abs=0.01)

def test_compute_eoq_holdingcost_zero():
    with pytest.raises(ValueError):
        compute_eoq(2000, 500, 0)

@pytest.fixture
def sample_dataframes():
    inventory_data = pd.DataFrame({
        "sku_id": ["SKU001"],
        "current_stock": [100],
        "opening_stock": [120],
        "avg_daily_demand": [10],
        "unit_cost": [50],
        "supplier_id": ["SUP001"]
    })

    suppliers_data = pd.DataFrame({
        "supplier_id": ["SUP001"],
        "avg_lead_time_days": [7]
    })

    sales_history_data = pd.DataFrame({
        "sku_id": ["SKU001", "SKU001"],
        "quantity_sold": [20, 30],
        "date": ["2026-07-01", "2026-07-15"]
    })
    return inventory_data, suppliers_data, sales_history_data

def test_compute_all_kpi_sku_exist(sample_dataframes):
    inventory_data, suppliers_data, sales_history_data = sample_dataframes
    results = compute_all_kpi(inventory_data, suppliers_data, sales_history_data)
    assert "SKU001" in results

def test_compute_all_kpi_returns_all_kpis(sample_dataframes):
    inventory_data, suppliers_data, sales_history_data = sample_dataframes
    results = compute_all_kpi(inventory_data, suppliers_data, sales_history_data)
    expected_keys = {"dos", "sop", "itr", "dsr", "rop", "ccp", "eoq"}

    assert expected_keys == set(results["SKU001"].keys())