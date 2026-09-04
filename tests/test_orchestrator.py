import pytest
import json
from pathlib import Path
from supplynode.agents.orchestrator import compute_composite_risk_score, save_alert, app


@pytest.fixture
def critical_stockout():
    return {"severity": "critical", "triggered": True, "findings": [], "recommendations": []}

@pytest.fixture
def critical_deadstock():
    return {"severity": "critical", "triggered": True, "findings": [], "recommendations": []}

@pytest.fixture
def critical_reorder():
    return {"severity": "critical", "triggered": True, "findings": []}

@pytest.fixture
def normal_stockout():
    return {"severity": "normal", "triggered": False, "findings": [], "recommendations": []}

@pytest.fixture
def normal_deadstock():
    return {"severity": "normal", "triggered": False, "findings": [], "recommendations": []}

@pytest.fixture
def normal_reorder():
    return {"severity": "normal", "triggered": False, "findings": []}


def test_compute_composite_risk_score_critical(critical_stockout, critical_deadstock, critical_reorder):
    assert compute_composite_risk_score(critical_stockout, critical_deadstock, critical_reorder) == 100.0

def test_compute_composite_risk_score_normal(normal_stockout, normal_deadstock, normal_reorder):
    assert compute_composite_risk_score(normal_stockout, normal_deadstock, normal_reorder) == 0.0

def test_compute_composite_risk_score_mixed(critical_stockout, normal_deadstock, normal_reorder):
    assert compute_composite_risk_score(critical_stockout, normal_deadstock, normal_reorder) == 50.0

@pytest.fixture
def test_state():
    return {
        "composite_risk_score": 0.85,
        "final_alert": "Critical inventory risk detected",
        "stockout_findings": {
            "triggered": True,
            "findings": [{"sku_id": "SKU001"}]
        },
        "deadstock_findings": {
            "triggered": False,
            "findings": []
        },
        "reorder_findings": {
            "triggered": True,
            "findings": [{"sku_id": "SKU001", "quantity": 100}]
        }
    }

def test_save_alert(tmp_path, monkeypatch, test_state):
    # Make the function use the temporary directory
    monkeypatch.chdir(tmp_path)

    filename = save_alert(test_state)

    # Check file exists
    assert Path(filename).exists()

    # Check JSON content
    with open(filename, "r") as f:
        output = json.load(f) # Loads json content and converts it to a Python dictionary

    assert output["risk_score"] == 0.85
    assert output["final_alert"] == "Critical inventory risk detected"

    assert output["stockout_findings"] == test_state["stockout_findings"]
    assert output["deadstock_findings"] == test_state["deadstock_findings"]
    assert output["reorder_findings"] == test_state["reorder_findings"]

    # Check timestamp exists
    assert "timestamp" in output

def test_graph_compiles():
    nodes = list(app.get_graph().nodes.keys())
    assert "kpi" in nodes
    assert "stockout" in nodes
    assert "deadstock" in nodes
    assert "reorder" in nodes
    assert "orchestrator" in nodes

def test_graph_edges():
    edges = [(e.source, e.target) for e in app.get_graph().edges]
    assert ("kpi", "stockout") in edges
    assert ("stockout", "deadstock") in edges
    assert ("deadstock", "reorder") in edges
    assert ("reorder", "orchestrator") in edges