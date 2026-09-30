from uuid import uuid4

from db.models import KPISnapshot, Alert
from db.repository import save_kpi_snapshots, save_alert_db
from supplynode.utils.db import SessionLocal


def test_save_kpi_snapshots():
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

    try:
        save_kpi_snapshots(run_id, kpi_results)

        session = SessionLocal()

        try:
            snapshot = (
                session.query(KPISnapshot)
                .filter_by(run_id=run_id)
                .first()
            )

            assert snapshot is not None
            assert snapshot.sku_id == "SKU001"
            assert snapshot.days_of_supply == 4.44

        finally:
            session.close()

    finally:
        session = SessionLocal()

        try:
            session.query(KPISnapshot).filter_by(
                run_id=run_id
            ).delete()

            session.commit()

        finally:
            session.close()

def test_save_alert():
    run_id = str(uuid4())

    findings = {
        "stockout": [],
        "dead_stock": [],
        "reorder": [],
    }

    try:
        save_alert_db(
            run_id=run_id,
            severity="CRITICAL",
            composite_risk_score=100.0,
            findings=findings,
            alert_message="Test alert",
        )

        session = SessionLocal()

        try:
            alert = (
                session.query(Alert)
                .filter_by(run_id=run_id)
                .first()
            )

            assert alert is not None
            assert alert.severity == "CRITICAL"
            assert alert.composite_risk_score == 100.0
            assert alert.findings == findings
            assert alert.alert_message == "Test alert"
            assert alert.status == "generated"

        finally:
            session.close()

    finally:
        session = SessionLocal()

        try:
            session.query(Alert).filter_by(
                run_id=run_id
            ).delete()

            session.commit()

        finally:
            session.close()