from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, UniqueConstraint, func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), default=None)
    status = Column(String(20), nullable=False, default="pending")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ProductValue(Base):
    __tablename__ = "product_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    column_id = Column(Integer, ForeignKey("template_columns.id", ondelete="CASCADE"), nullable=False)
    value = Column(Text, default=None)

    __table_args__ = (
        UniqueConstraint("product_id", "column_id", name="uq_product_column"),
    )


class ExportLog(Base):
    __tablename__ = "export_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exported_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    filename = Column(String(300))
    total_products = Column(Integer, default=0)
    filter_used = Column(String(500), default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())
