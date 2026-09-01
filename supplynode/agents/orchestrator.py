import pandas as pd
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from ..engine import compute_all_kpi
from .stockout_engine import stockout_prevention
from .deadstock_engine import deadstock_detection
from .reorder_engine import reorder_optimization

class SupplyNodeState(TypedDict):
    """
    A TypedDict representing the state of a supply node agent.
    """

    # Input data
    inventory_df: Any
    suppliers_df: Any
    sales_df: Any

    # After kpi node
    kpi_results: Dict[str, Any]

    # After engines nodes
    stockout_findings: Dict[str, Any]
    deadstock_findings: Dict[str, Any]
    reorder_findings: Dict[str, Any]

    # After orchestration node
    composite_risk_score: float
    final_alert: str
    alert_metadata: Dict[str, Any]

def node_kpi(state: SupplyNodeState) -> SupplyNodeState:
    state["kpi_results"] = compute_all_kpi(
        state["inventory_df"],
        state["suppliers_df"], 
        state["sales_df"]
    )
    return state

def node_stockout(state: SupplyNodeState) -> SupplyNodeState:
    state["stockout_findings"] = stockout_prevention(
        state["kpi_results"],
        state["inventory_df"]
    )
    return state

def node_deadstock(state: SupplyNodeState) -> SupplyNodeState:
    state["deadstock_findings"] = deadstock_detection(
        state["kpi_results"],
        state["inventory_df"]
    )
    return state

def node_reorder(state: SupplyNodeState) -> SupplyNodeState:
    state["reorder_findings"] = reorder_optimization(
        state["stockout_findings"],
        state["kpi_results"], 
        state["inventory_df"], 
        state["suppliers_df"]
    )
    return state

def node_orchestrator(state: SupplyNodeState) -> SupplyNodeState:
    state["composite_risk_score"] = 0.0 # Implemented in commit 2
    state["final_alert"] = "" # Implemented in commit 3
    state["alert_metadata"] = {} # Implemented in commit 4
    return state

# Build and compile the LangGraph agent graph
workflow = StateGraph(SupplyNodeState)
workflow.add_node("kpi", node_kpi)
workflow.add_node("stockout", node_stockout)
workflow.add_node("deadstock", node_deadstock)
workflow.add_node("reorder", node_reorder)
workflow.add_node("orchestrator", node_orchestrator)

workflow.set_entry_point("kpi")
workflow.add_edge("kpi", "stockout")
workflow.add_edge("stockout", "deadstock")
workflow.add_edge("deadstock", "reorder")
workflow.add_edge("reorder", "orchestrator")
workflow.add_edge("orchestrator", END)

app = workflow.compile()
