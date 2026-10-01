from sqlalchemy import inspect, text

from db.models import Alert, Inventory, KPISnapshot, SalesHistory, Supplier, Override


def test_database_connection(test_session):
    result = test_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_all_required_tables_exist(test_session):
    inspector = inspect(test_session.bind)

    tables = set(inspector.get_table_names())

    expected_tables = {
        "alerts",
        "suppliers",
        "inventory",
        "kpi_snapshots",
        "overrides",
        "sales_history",
    }

    assert expected_tables.issubset(tables)


def test_primary_keys(test_session):
    inspector = inspect(test_session.bind)

    expected_primary_keys = {
        "alerts": ["id"],
        "suppliers": ["supplier_id"],
        "inventory": ["sku_id"],
        "kpi_snapshots": ["id"],
        "overrides": ["id"],
        "sales_history": ["transaction_id"],
    }

    for table, expected_columns in expected_primary_keys.items():
        pk = inspector.get_pk_constraint(table)
        assert pk["constrained_columns"] == expected_columns


def test_foreign_keys(test_session):
    inspector = inspect(test_session.bind)

    inventory_fks = inspector.get_foreign_keys("inventory")
    assert any(
        fk["constrained_columns"] == ["supplier_id"]
        and fk["referred_table"] == "suppliers"
        and fk["referred_columns"] == ["supplier_id"]
        for fk in inventory_fks
    )

    kpi_fks = inspector.get_foreign_keys("kpi_snapshots")
    assert any(
        fk["constrained_columns"] == ["sku_id"]
        and fk["referred_table"] == "inventory"
        and fk["referred_columns"] == ["sku_id"]
        for fk in kpi_fks
    )

    sales_fks = inspector.get_foreign_keys("sales_history")
    assert any(
        fk["constrained_columns"] == ["sku_id"]
        and fk["referred_table"] == "inventory"
        and fk["referred_columns"] == ["sku_id"]
        for fk in sales_fks
    )

    override_fks = inspector.get_foreign_keys("overrides")
    assert any(
        fk["constrained_columns"] == ["sku_id"]
        and fk["referred_table"] == "inventory"
        and fk["referred_columns"] == ["sku_id"]
        for fk in override_fks
    )