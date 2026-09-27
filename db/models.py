from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String, primary_key=True)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)

    contact_person: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(String, nullable=True)
    gstin: Mapped[str | None] = mapped_column(String, nullable=True)

    payment_terms_days: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    avg_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reliability_score: Mapped[float] = mapped_column(Float, nullable=False)
    minimum_order_value: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

class Inventory(Base):
    __tablename__ = "inventory"

    __table_args__ = (
        Index("ix_inventory_supplier_id", "supplier_id"),
    )

    sku_id: Mapped[str] = mapped_column(String, primary_key=True)
    sku_name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    uom: Mapped[str] = mapped_column(String, nullable=False)
    hsn_code: Mapped[str] = mapped_column(String, nullable=False)

    gst_rate: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False)

    current_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_daily_demand: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    supplier_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("suppliers.supplier_id"),
        nullable=False,
    )

    warehouse_location: Mapped[str] = mapped_column(String, nullable=False)
    last_purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    opening_stock: Mapped[int] = mapped_column(Integer, nullable=False)

class SalesHistory(Base):
    __tablename__ = "sales_history"

    __table_args__ = (
        Index("ix_sales_history_sku_id", "sku_id"),
    )

    transaction_id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    invoice_no: Mapped[str] = mapped_column(String, nullable=False)

    sku_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("inventory.sku_id"), 
        nullable=False
    )

    customer_id: Mapped[str] = mapped_column(String, nullable=False)
    quantity_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=False)
    gst: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)

class KPISnapshot(Base):
    __tablename__ = "kpi_snapshots"

    __table_args__ = (
        UniqueConstraint("run_id", "sku_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, nullable=False)
    sku_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("inventory.sku_id"), 
        nullable=False
    )

    days_of_supply: Mapped[float] = mapped_column(Float, nullable=False)
    stockout_probability: Mapped[float] = mapped_column(Float, nullable=False)
    inventory_turnover_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    dead_stock_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    carrying_cost_pct: Mapped[float] = mapped_column(Float, nullable=False)
    order_fill_rate_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    forecast_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    economic_order_quantity: Mapped[float] = mapped_column(Float, nullable=False)

    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    composite_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    findings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    alert_message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class Override(Base):
    __tablename__ = "overrides"

    __table_args__ = (
        Index("ix_overrides_run_id", "run_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(String, nullable=False)
    sku_id: Mapped[str] = mapped_column(
        String, ForeignKey("inventory.sku_id"), 
        nullable=False
    )

    original_recommendation: Mapped[dict] = mapped_column(JSONB, nullable=False)
    override_value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
