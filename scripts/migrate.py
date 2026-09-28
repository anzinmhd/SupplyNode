import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from supplynode.data.loader import read_inventory_data
from supplynode.utils.db import SessionLocal
from db.models import Supplier, Inventory, SalesHistory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = PROJECT_ROOT / "supplynode" / "data" / "sample_data.xlsx"

if not EXCEL_PATH.exists():
    raise FileNotFoundError(f"Excel file not found: {EXCEL_PATH}")

inventory_df, suppliers_df, sales_history_df = read_inventory_data(
    str(EXCEL_PATH)
)


print(f"Inventory records: {len(inventory_df)}")
print(f"Supplier records: {len(suppliers_df)}")
print(f"Sales history records: {len(sales_history_df)}")

session = SessionLocal()

try:

    for _, row in suppliers_df.iterrows():
        existing_supplier = session.get(
            Supplier,
            row["supplier_id"]
        )

        if existing_supplier:
            print(
                f"Supplier {row['supplier_id']} already exists — skipping"
            )
            continue

        supplier = Supplier(
            supplier_id=row["supplier_id"],
            supplier_name=row["supplier_name"],
            contact_person=row["contact_person"],
            phone=row["phone"],
            email=row["email"],
            address=row["address"],
            gstin=row["gstin"],
            payment_terms_days=row["payment_terms_days"],
            avg_lead_time_days=row["avg_lead_time_days"],
            reliability_score=row["reliability_score"],
            minimum_order_value=row["minimum_order_value"],
            active=row["active"],
        )

        session.add(supplier)

    for _, row in inventory_df.iterrows():
        existing_inventory = session.get(
            Inventory,
            row["sku_id"]
        )

        if existing_inventory:
            print(f"Inventory {row['sku_id']} already exists — skipping")
            continue

        inventory = Inventory(
            sku_id=row["sku_id"],
            sku_name=row["sku_name"],
            category=row["category"],
            brand=row["brand"],
            uom=row["uom"],
            hsn_code=row["hsn_code"],
            gst_rate=row["gst_rate"],
            unit_cost=row["unit_cost"],
            selling_price=row["selling_price"],
            current_stock=row["current_stock"],
            avg_daily_demand=row["avg_daily_demand"],
            reorder_point=row["reorder_point"],
            reorder_quantity=row["reorder_quantity"],
            supplier_id=row["supplier_id"],
            warehouse_location=row["warehouse_location"],
            last_purchase_date=row["last_purchase_date"],
            active=row["active"],
            opening_stock=row["opening_stock"],
        )

        session.add(inventory)

    for _, row in sales_history_df.iterrows():
        existing_sale = session.get(
            SalesHistory,
            row["transaction_id"]
        )

        if existing_sale:
            print(
                f"Sales transaction {row['transaction_id']} "
                f"already exists — skipping"
            )
            continue

        sales_history = SalesHistory(
            transaction_id=row["transaction_id"],
            date=row["date"],
            invoice_no=row["invoice_no"],
            sku_id=row["sku_id"],
            customer_id=row["customer_id"],
            quantity_sold=row["quantity_sold"],
            unit_price=row["unit_price"],
            discount=row["discount"],
            gst=row["gst"],
            total_amount=row["total_amount"],
        )

        session.add(sales_history)

    session.commit()
    print("Migration completed successfully.")

except Exception as e:
    session.rollback()
    print(f"Migration failed: {e}")
    raise

finally:
    session.close()