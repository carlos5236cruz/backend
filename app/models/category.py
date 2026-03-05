from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, func
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())


class CategoryAttribute(Base):
    __tablename__ = "category_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    attribute_name = Column(String(200), nullable=False)
    default_value = Column(String(500), default=None)
