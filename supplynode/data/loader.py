import os
import warnings
import pandas as pd
from typing import Tuple



def read_inventory_data(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads inventory, supplier, and sales history data
    from an Excel file and returns them as pandas DataFrames.

    Parameters:
    file_path (str): The path to the Excel file containing inventory data.

    Returns:
    A tuple containing three DataFrames (inventory_data, suppliers_data, sales_history_data).
    Each DataFrame corresponds to a sheet in the Excel file:
    """
    try:
        # Check file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found : {file_path}")

        # Read the inventory sheet into a DataFrame
        inventory_data = pd.read_excel(file_path, sheet_name="inventory", engine="openpyxl")
        #fill NaN values of numeric colums with 0
        cols_numeric = inventory_data.select_dtypes(include="number").columns
        inventory_data[cols_numeric] = inventory_data[cols_numeric].fillna(0)
        # Convert data types
        inventory_data = inventory_data.astype({"current_stock": "int64", "unit_cost" : "float64"})
        # Warning if any sku_id is NaN or if any avg_daily_demand is 0
        if inventory_data["sku_id"].isna().any():
            warnings.warn("Some sku_id values are NaN in the inventory data.")
        if (inventory_data["avg_daily_demand"]==0).any():
            warnings.warn("Some avg_daily_demand values are 0 in the inventory data.")

        # Read the suppliers sheet into a DataFrame
        suppliers_data = pd.read_excel(file_path, sheet_name="suppliers", engine="openpyxl")
        #fill NaN values of numeric colums with 0
        cols_numeric = suppliers_data.select_dtypes(include="number").columns
        suppliers_data[cols_numeric] = suppliers_data[cols_numeric].fillna(0)
        # Convert data types
        suppliers_data = suppliers_data.astype({"avg_lead_time_days" : "int64", "reliability_score" : "float64"})
        # Warning if any supplier_id is NaN or if any avg_lead_time_days is 0
        if suppliers_data["supplier_id"].isna().any():
            warnings.warn("Some supplier_id values are NaN in the suppliers data.")
        if (suppliers_data["avg_lead_time_days"]==0).any():
            warnings.warn("Some avg_lead_time_days values are 0 in the suppliers data.")

        # Read the sales_history sheet into a DataFrame
        sales_history_data = pd.read_excel(file_path, sheet_name="sales_history", engine="openpyxl")
        #fill NaN values of numeric colums with 0
        cols_numeric = sales_history_data.select_dtypes(include="number").columns
        sales_history_data[cols_numeric] = sales_history_data[cols_numeric].fillna(0)
        # Convert data types
        sales_history_data = sales_history_data.astype({"quantity_sold" : "int64", "unit_price" : "float64"})
        # Warning if any sku_id is NaN or if any quantity_sold is 0
        if sales_history_data["sku_id"].isna().any():
            warnings.warn("Some sku_id values are NaN in the sales_history data.")
        if (sales_history_data["quantity_sold"]==0).any():
            warnings.warn("Some quantity_sold values are 0 in the sales_history data.")

        # Return the DataFrames
        return inventory_data, suppliers_data, sales_history_data

    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error reading inventory data: {e}") from e
