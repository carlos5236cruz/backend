from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    original_filename = Column(String(300), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class TemplateColumn(Base):
    __tablename__ = "template_columns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    column_name = Column(String(200), nullable=False)
    column_order = Column(Integer, nullable=False)
    data_type = Column(String(50), default="text")
