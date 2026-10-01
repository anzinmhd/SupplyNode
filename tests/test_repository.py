from uuid import uuid4

from db.models import KPISnapshot, Alert
from db.repository import save_kpi_snapshots, save_alert_db


def test_save_kpi_snapshots(test_session):
    run_id = str(uuid4())

    kpi_results = {
        "SKU001": {
            "dos": 4.44,
            "sop": 0.1,
            "itr": 1.5,
            "dsr": 0.0,
            "rop": 162.0,
            "ccp": 25.0,
            "eoq": 900.0,
        }
    }


    save_kpi_snapshots(
        run_id,
        kpi_results,
        session=test_session,
    )


    snapshot = (
        test_session.query(KPISnapshot)
        .filter_by(run_id=run_id)
        .first()
    )

    assert snapshot is not None
    assert snapshot.sku_id == "SKU001"
    assert snapshot.days_of_supply == 4.44

def test_save_alert(test_session):
    run_id = str(uuid4())

    findings = {
        "stockout": [],
        "dead_stock": [],
        "reorder": [],
    }

    save_alert_db(
            run_id=run_id,
            severity="CRITICAL",
            composite_risk_score=100.0,
            findings=findings,
            alert_message="Test alert",
            session=test_session
    )

    alert = (
        test_session.query(Alert)
        .filter_by(run_id=run_id)
        .first()
    )

    assert alert is not None
    assert alert.severity == "CRITICAL"
    assert alert.composite_risk_score == 100.0
    assert alert.findings == findings
    assert alert.alert_message == "Test alert"
    assert alert.status == "generated"