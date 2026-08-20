import os
import pytest
import pandas as pd
from supplynode.data import read_inventory_data

FILE_PATH = os.path.join(
    os.path.dirname(__file__), # tests/directory
    "..", # upto project root
    "supplynode", "data", "sample_data.xlsx"
)

# Checks if three dataframes are returned
def test_returns_three_dataframes():
    inventory_data, supplier_data, sales_history_data = read_inventory_data(FILE_PATH)
    assert isinstance(inventory_data, pd.DataFrame)
    assert isinstance(supplier_data, pd.DataFrame)
    assert isinstance(sales_history_data, pd.DataFrame)

# Checks checks error handling when file doesn't exist
def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_inventory_data("wrongpath.xlsx")

# Checks dtypes of specified columns
def test_dtype_specific_columns():
    inventory_data, supplier_data, sales_history_data = read_inventory_data(FILE_PATH)
    assert inventory_data["current_stock"].dtype == "int64"
    assert inventory_data["unit_cost"].dtype == "float64"
    assert supplier_data["avg_lead_time_days"].dtype == "int64"
    assert supplier_data["reliability_score"].dtype == "float64"
    assert sales_history_data["quantity_sold"].dtype == "int64"
    assert sales_history_data["unit_price"].dtype == "float64"

# Checks NaN in numeric columns
def test_nan_numeric_columns():
    inventory_data, supplier_data, sales_history_data = read_inventory_data(FILE_PATH)
    cols_numeric = inventory_data.select_dtypes(include="number").columns
    assert  not inventory_data[cols_numeric].isna().any().any()
    cols_numeric = supplier_data.select_dtypes(include="number").columns
    assert not supplier_data[cols_numeric].isna().any().any()
    cols_numeric = sales_history_data.select_dtypes(include="number").columns
    assert not sales_history_data[cols_numeric].isna().any().any()

# Checks if required columns exists
def test_required_columns_exists():
    inventory_data, suppliers_data, sales_history_data = read_inventory_data(FILE_PATH)
    assert "sku_id" in inventory_data.columns
    assert "current_stock" in inventory_data.columns
    assert "avg_daily_demand" in inventory_data.columns
    assert "supplier_id" in suppliers_data.columns
    assert "reliability_score" in suppliers_data.columns
    assert "quantity_sold" in sales_history_data.columns
