import pytest
import pandas as pd
from supplynode.agents import (stockout_prevention,
                               deadstock_detection,
                               reorder_optimization
)
from supplynode.engine import compute_all_kpi

@pytest.fixture
def sample_inventory_data():
    inventory_data = pd.DataFrame({
        "sku_id": ["SKU001", "SKU002", "SKU003", "SKU004", "SKU005"],
        "sku_name": ["Turmeric 500g", "Black Pepper 250g", "Cardamom 100g", "Coconut Oil 1L", "Rice 5kg"],
        "current_stock": [200, 800, 45, 30, 1200],
        "opening_stock": [1550, 1250, 410, 270, 2400],
        "avg_daily_demand": [45, 15, 12, 8, 40],
        "unit_cost": [82, 165, 310, 138, 265],
        "supplier_id": ["SUP001", "SUP002", "SUP002", "SUP003", "SUP001"],
        "last_purchase_date": [
            "2026-07-25", "2026-07-20", "2026-07-18", "2026-07-28", "2026-07-30"
        ]
    })
    return inventory_data

@pytest.fixture
def sample_supplier_data():
    supplier_data = pd.DataFrame({
        "supplier_id": ["SUP001", "SUP002", "SUP003"],
        "supplier_name": ["Kerala Agro Distributors", "Malabar Foods & Spices", "South India Wholesale Hub"],
        "avg_lead_time_days": [3, 6, 10],
        "reliability_score": [0.94, 0.86, 0.72]
    })
    return supplier_data

@pytest.fixture
def sample_kpi_results():
    kpi_results = {
        "SKU001": {
            "dos": 4.44,
            "sop": 0.0,
            "itr": 1.56,
            "dsr": 0.0,
            "rop": 162.0,
            "ccp": 25.0,
            "eoq": 900.4
        },
        "SKU002": {
            "dos": 53.33,
            "sop": 0.0,
            "itr": 0.44,
            "dsr": 0.0,
            "rop": 108.0,
            "ccp": 25.0,
            "eoq": 363.1
        },
        "SKU003": {
            "dos": 3.75,
            "sop": 1.0,
            "itr": 1.59,
            "dsr": 0.0,
            "rop": 86.4,
            "ccp": 25.0,
            "eoq": 238.39
        },
        "SKU004": {
            "dos": 3.75,
            "sop": 1.0,
            "itr": 4.67,
            "dsr": 0.0,
            "rop": 96.0,
            "ccp": 25.0,
            "eoq": 282.94
        },
        "SKU005": {
            "dos": 30.0,
            "sop": 0.0,
            "itr": 0.65,
            "dsr": 0.0,
            "rop": 144.0,
            "ccp": 25.0,
            "eoq": 462.75
        }
    }

    return kpi_results

# stockout_engine

def test_stockout_triggered(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    assert result["triggered"] is True

def test_stockout_severity_critical(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    assert result["severity"] == "critical"

def test_stockout_flagged_skus(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU001" in flagged_ids
    assert "SKU003" in flagged_ids
    assert "SKU004" in flagged_ids

def test_stockout_healthy_skus_not_flagged(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU002" not in flagged_ids
    assert "SKU005" not in flagged_ids

def test_stockout_risk_level(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    critical_skus = [f["sku_id"] for f in result["findings"] if f["risk_level"] == "critical"]
    assert "SKU001" in critical_skus
    assert "SKU003" in critical_skus
    assert "SKU004" in critical_skus

def test_stockout_recommendations_generated(sample_kpi_results, sample_inventory_data):
    result = stockout_prevention(sample_kpi_results, sample_inventory_data)
    rec_ids = [r["sku_id"] for r in result["recommendations"]]
    assert "SKU001" in rec_ids
    assert "SKU003" in rec_ids
    assert "SKU004" in rec_ids

def test_stockout_not_triggered_when_healthy():
    healthy_kpi = {
        "SKU001": {"dos": 30.0, "sop": 0.0, "itr": 5.0,
                   "dsr": 0.0, "rop": 90.0, "ccp": 25.0, "eoq": 500.0}
    }
    healthy_inv = pd.DataFrame({
        "sku_id": ["SKU001"],
        "sku_name": ["Test SKU"],
        "current_stock": [1200],
        "avg_daily_demand": [40],
        "unit_cost": [100],
        "supplier_id": ["SUP001"]
    })
    result = stockout_prevention(healthy_kpi, healthy_inv)
    assert result["triggered"] is False
    assert result["severity"] == "normal"

# deadstock_engine

def test_deadstock_triggered(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    assert result["triggered"] is True

def test_deadstock_severity_critical(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    assert result["severity"] == "critical"

def test_deadstock_flagged_sku(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU001" in flagged_ids
    assert "SKU002" in flagged_ids
    assert "SKU003" in flagged_ids
    assert "SKU005" in flagged_ids

def test_deadstock_unflagged_sku(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU004" not in flagged_ids


def test_deadstock_critical_sku(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    critical_ids = [f["sku_id"] for f in result["findings"] if f["risk_level"] == "critical"]
    assert "SKU002" in critical_ids
    assert "SKU005" in critical_ids

def test_deadstock_recommendations_generated(sample_kpi_results, sample_inventory_data):
    result = deadstock_detection(sample_kpi_results, sample_inventory_data)
    rec_ids = [r["sku_id"] for r in result["recommendations"]]
    assert "SKU001" in rec_ids
    assert "SKU002" in rec_ids
    assert "SKU003" in rec_ids
    assert "SKU005" in rec_ids

def test_deadstock_not_triggered_when_healthy():
    healthy_kpi = {
        "SKU001": {"dos": 30.0, "sop": 0.0, "itr": 5.0,
                   "dsr": 0.0, "rop": 90.0, "ccp": 25.0, "eoq": 500.0}
    }
    healthy_inv = pd.DataFrame({
        "sku_id": ["SKU001"],
        "sku_name": ["Test SKU"],
        "current_stock": [1200],
        "avg_daily_demand": [40],
        "unit_cost": [100],
        "supplier_id": ["SUP001"],
        "last_purchase_date": ["2026-01-15"]
    })
    result = deadstock_detection(healthy_kpi, healthy_inv)
    assert result["triggered"] is False
    assert result["severity"] == "normal"

# reorder_engine

@pytest.fixture
def sample_stockout_results():
    return {
        "engine_name": "stockout_prevention",
        "triggered": True,
        "severity": "critical",
        "findings": [
            {
                "sku_id": "SKU001",
                "sku_name": "Turmeric 500g",
                "days_of_supply": 4.44,
                "stockout_probability": 0.0,
                "risk_level": "critical"
            },
            {
                "sku_id": "SKU003",
                "sku_name": "Cardamom 100g",
                "days_of_supply": 3.75,
                "stockout_probability": 1.0,
                "risk_level": "critical"
            },
            {
                "sku_id": "SKU004",
                "sku_name": "Coconut Oil 1L",
                "days_of_supply": 10,
                "stockout_probability": 1.0,
                "risk_level": "normal"
            }
        ],
        "recommendations": [
            {
                "sku_id": "SKU001",
                "sku_name": "Turmeric 500g",
                "action": "reorder",
                "quantity": 900.4,
                "supplier": "SUP001",
                "estimated_cost": 73832.8
            },
            {
                "sku_id": "SKU003",
                "sku_name": "Cardamom 100g",
                "action": "reorder",
                "quantity": 238.39,
                "supplier": "SUP002",
                "estimated_cost": 73900.9
            },
            {
                "sku_id": "SKU004",
                "sku_name": "Coconut Oil 1L",
                "action": "reorder",
                "quantity": 282.94,
                "supplier": "SUP003",
                "estimated_cost": 39045.72
            }
        ]
    }

def test_reorder_triggered(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    assert result["triggered"] is True

def test_reorder_severity_critical(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    assert result["severity"] == "critical"

def test_reorder_flagged_sku(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU001" in flagged_ids
    assert "SKU003" in flagged_ids

def test_reorder_unflagged_sku(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    flagged_ids = [f["sku_id"] for f in result["findings"]]
    assert "SKU004" not in flagged_ids


def test_reorder_urgency_immediate(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    immediate_ids = [f["sku_id"] for f in result["findings"] if f["urgency"] == "immediate"]
    assert "SKU001" in immediate_ids
    assert "SKU003" in immediate_ids

def test_reorder_urgency_not_immediate(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data):
    result = reorder_optimization(sample_stockout_results, sample_kpi_results, sample_inventory_data, sample_supplier_data)
    immediate_ids = [f["sku_id"] for f in result["findings"] if f["urgency"] == "immediate"]
    assert "SKU004" not in immediate_ids

def test_reorder_not_triggered_when_healthy():
    healthy_stout = {
        "engine_name": "stockout_prevention",
        "triggered": False,
        "severity": "normal",
        "findings": [
            {
                "sku_id": "SKU001",
                "sku_name": "Coconut Oil 1L",
                "days_of_supply": 10,
                "stockout_probability": 1.0,
                "risk_level": "normal"
            }
        ],
        "recommendations": [
            {
                "sku_id": "SKU001",
                "sku_name": "Coconut Oil 1L",
                "action": "reorder",
                "quantity": 282.94,
                "supplier": "SUP003",
                "estimated_cost": 39045.72
            }
        ]
    }
    healthy_kpi = {
        "SKU001": {"dos": 30.0, "sop": 0.0, "itr": 5.0,
                   "dsr": 0.0, "rop": 90.0, "ccp": 25.0, "eoq": 500.0}
    }
    healthy_inv = pd.DataFrame({
        "sku_id": ["SKU001"],
        "sku_name": ["Test SKU"],
        "current_stock": [1200],
        "avg_daily_demand": [40],
        "unit_cost": [100],
        "supplier_id": ["SUP001"],
        "last_purchase_date": ["2026-01-15"]
    })
    healthy_supp = pd.DataFrame({
        "supplier_id":["SUP001"],
        "avg_lead_time_days": [7],
        "reliability_score": [0.67]
    })
    result = reorder_optimization(healthy_stout, healthy_kpi, healthy_inv, healthy_supp)
    assert result["triggered"] is False
    assert result["severity"] == "normal"