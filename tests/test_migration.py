from sqlalchemy import func

from db.models import Supplier, Inventory, SalesHistory


def test_expected_suppliers_migrated(test_session):
    assert test_session.query(Supplier).count() == 3

    supplier_ids = {
        supplier.supplier_id
        for supplier in test_session.query(Supplier).all()
    }

    assert supplier_ids == {"SUP001", "SUP002", "SUP003"}


def test_expected_inventory_migrated(test_session):
    assert test_session.query(Inventory).count() == 5

    sku_ids = {
        inventory.sku_id
        for inventory in test_session.query(Inventory).all()
    }

    assert sku_ids == {
        "SKU001",
        "SKU002",
        "SKU003",
        "SKU004",
        "SKU005",
    }


def test_expected_sales_history_migrated(test_session):
    assert test_session.query(SalesHistory).count() == 150


def test_migration_data_has_no_duplicates(test_session):
    supplier_duplicates = (
        test_session.query(
            Supplier.supplier_id,
            func.count(Supplier.supplier_id),
        )
        .group_by(Supplier.supplier_id)
        .having(func.count(Supplier.supplier_id) > 1)
        .all()
    )

    inventory_duplicates = (
        test_session.query(
            Inventory.sku_id,
            func.count(Inventory.sku_id),
        )
        .group_by(Inventory.sku_id)
        .having(func.count(Inventory.sku_id) > 1)
        .all()
    )

    sales_duplicates = (
        test_session.query(
            SalesHistory.transaction_id,
            func.count(SalesHistory.transaction_id),
        )
        .group_by(SalesHistory.transaction_id)
        .having(func.count(SalesHistory.transaction_id) > 1)
        .all()
    )

    assert supplier_duplicates == []
    assert inventory_duplicates == []
    assert sales_duplicates == []