from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from io import BytesIO
from app.database import get_db
from app.models.user import User
from app.models.template import Template, TemplateColumn
from app.models.product import Product, ProductValue, ExportLog
from app.models.category import Category
from app.utils.security import require_admin
from app.utils.excel import generate_export_excel

router = APIRouter(prefix="/api/export", tags=["Export"])

CATEGORY_COLUMN_NAME = "Categoria do produto"


def _get_category_path(category_id, db):
    if not category_id:
        return ""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        return ""
    if cat.parent_id:
        parent = db.query(Category).filter(Category.id == cat.parent_id).first()
        if parent:
            return f"{parent.name}>>{cat.name}"
    return cat.name


@router.post("")
def export_products(
    status_filter: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    active_template = db.query(Template).filter(Template.is_active == True).first()
    if not active_template:
        raise HTTPException(status_code=400, detail="Nenhum template ativo")

    columns = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == active_template.id
    ).order_by(TemplateColumn.column_order).all()

    col_names = [c.column_name for c in columns]
    col_id_to_name = {c.id: c.column_name for c in columns}

    query = db.query(Product).filter(Product.template_id == active_template.id)
    if status_filter:
        query = query.filter(Product.status == status_filter)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    products = query.all()
    products_data = []

    for product in products:
        row = {col: "" for col in col_names}
        values = db.query(ProductValue).filter(ProductValue.product_id == product.id).all()
        for v in values:
            if v.column_id in col_id_to_name:
                row[col_id_to_name[v.column_id]] = v.value or ""
        if CATEGORY_COLUMN_NAME in row:
            row[CATEGORY_COLUMN_NAME] = _get_category_path(product.category_id, db)
        products_data.append(row)

    excel_bytes = generate_export_excel(col_names, products_data)

    filter_desc = []
    if status_filter:
        filter_desc.append(f"status={status_filter}")
    if category_id:
        filter_desc.append(f"category={category_id}")

    log = ExportLog(
        exported_by=current_user.id,
        filename=f"export_{active_template.name}.xlsx",
        total_products=len(products_data),
        filter_used=", ".join(filter_desc) if filter_desc else None
    )
    db.add(log)
    db.commit()

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=export_{active_template.name}.xlsx"}
    )


@router.get("/logs")
def export_logs(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    logs = db.query(ExportLog).order_by(ExportLog.created_at.desc()).limit(50).all()
    return [{
        "id": log.id,
        "exported_by": log.exported_by,
        "filename": log.filename,
        "total_products": log.total_products,
        "filter_used": log.filter_used,
        "created_at": log.created_at.isoformat() if log.created_at else None
    } for log in logs]
