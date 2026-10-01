from datetime import datetime
from supplynode.utils.db import SessionLocal
from db.models import KPISnapshot, Alert

def save_kpi_snapshots(
    run_id: str,
    kpi_results: dict,
    session=None,
):
    """Persist KPI results for a pipeline run to the database."""

    own_session = session is None

    if own_session:
        session = SessionLocal()

    try:
        for sku_id, metrics in kpi_results.items():
            snapshot = KPISnapshot(
                run_id=run_id,
                sku_id=sku_id,
                days_of_supply=float(metrics["dos"]),
                stockout_probability=float(metrics["sop"]),
                inventory_turnover_ratio=float(metrics["itr"]),
                dead_stock_ratio=float(metrics["dsr"]),
                reorder_point=float(metrics["rop"]),
                carrying_cost_pct=float(metrics["ccp"]),
                order_fill_rate_pct=None,
                forecast_accuracy=None,
                economic_order_quantity=float(metrics["eoq"]),
                computed_at=datetime.now(),
            )
            session.add(snapshot)

        if own_session:
            session.commit()

    except Exception:
        if own_session:
            session.rollback()
        raise

    finally:
        if own_session:
            session.close()

def save_alert_db(
    run_id: str,
    severity: str,
    composite_risk_score: float,
    findings: dict,
    alert_message: str,
    status: str = "generated",
    session=None,
):
    """Persist the final SupplyNode alert for a pipeline run to the database."""
    
    own_session = session is None
    if own_session:
        session = SessionLocal()

    try:
        alert = Alert(
            run_id=run_id,
            severity=severity,
            composite_risk_score=float(composite_risk_score),
            findings=findings,
            alert_message=alert_message,
            status=status,
            created_at=datetime.now(),
        )

        session.add(alert)
        if own_session:
            session.commit()

    except Exception:
        if own_session:
            session.rollback()
        raise

    finally:
        if own_session:
            session.close()
