from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.template import Template, TemplateColumn
from app.models.product import Product, ProductValue
from app.models.category import Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductListResponse, ProductValueResponse, BulkImportResponse
)
from app.utils.security import get_current_user
from app.utils.excel import read_excel_products

router = APIRouter(prefix="/api/products", tags=["Products"])


def _build_product_response(product: Product, db: Session) -> ProductResponse:
    values = db.query(ProductValue, TemplateColumn).join(
        TemplateColumn, ProductValue.column_id == TemplateColumn.id
    ).filter(ProductValue.product_id == product.id).order_by(TemplateColumn.column_order).all()

    category_name = None
    if product.category_id:
        cat = db.query(Category).filter(Category.id == product.category_id).first()
        if cat:
            category_name = cat.name

    return ProductResponse(
        id=product.id,
        template_id=product.template_id,
        category_id=product.category_id,
        category_name=category_name,
        status=product.status,
        created_by=product.created_by,
        updated_by=product.updated_by,
        created_at=product.created_at,
        updated_at=product.updated_at,
        values=[ProductValueResponse(
            column_id=pv.id,
            column_name=tc.column_name,
            value=pv.value
        ) for pv, tc in values]
    )


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_template = db.query(Template).filter(Template.is_active == True).first()
    if not active_template:
        return ProductListResponse(products=[], total=0, page=page, per_page=per_page)

    query = db.query(Product).filter(Product.template_id == active_template.id)

    if status:
        query = query.filter(Product.status == status)
    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        product_ids = db.query(ProductValue.product_id).filter(
            ProductValue.value.like(f"%{search}%")
        ).distinct().subquery()
        query = query.filter(Product.id.in_(db.query(product_ids)))

    total = query.count()
    products = query.order_by(Product.updated_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return ProductListResponse(
        products=[_build_product_response(p, db) for p in products],
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_template = db.query(Template).filter(Template.is_active == True).first()
    if not active_template:
        raise HTTPException(status_code=400, detail="Nenhum template ativo. Faça upload de um template primeiro.")

    product = Product(
        template_id=active_template.id,
        category_id=data.category_id,
        created_by=current_user.id,
        status="pending"
    )
    db.add(product)
    db.flush()

    columns = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == active_template.id
    ).all()
    col_map = {c.column_name: c.id for c in columns}

    for col_name, value in data.values.items():
        if col_name in col_map:
            pv = ProductValue(product_id=product.id, column_id=col_map[col_name], value=value)
            db.add(pv)

    db.commit()
    db.refresh(product)
    return _build_product_response(product, db)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if data.category_id is not None:
        product.category_id = data.category_id
    if data.status is not None:
        product.status = data.status

    product.updated_by = current_user.id

    if data.values:
        columns = db.query(TemplateColumn).filter(
            TemplateColumn.template_id == product.template_id
        ).all()
        col_map = {c.column_name: c.id for c in columns}

        for col_name, value in data.values.items():
            if col_name in col_map:
                existing = db.query(ProductValue).filter(
                    ProductValue.product_id == product.id,
                    ProductValue.column_id == col_map[col_name]
                ).first()
                if existing:
                    existing.value = value
                else:
                    pv = ProductValue(product_id=product.id, column_id=col_map[col_name], value=value)
                    db.add(pv)

    db.commit()
    db.refresh(product)
    return _build_product_response(product, db)


@router.put("/{product_id}/status")
def update_product_status(
    product_id: int,
    status: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product.status = status
    product.updated_by = current_user.id
    db.commit()
    return {"message": f"Status atualizado para {status}"}


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(product)
    db.commit()
    return {"message": "Produto removido"}


@router.post("/import", response_model=BulkImportResponse)
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    active_template = db.query(Template).filter(Template.is_active == True).first()
    if not active_template:
        raise HTTPException(status_code=400, detail="Nenhum template ativo")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel (.xlsx, .xls)")

    file_bytes = await file.read()
    try:
        rows = read_excel_products(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {str(e)}")

    columns = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == active_template.id
    ).all()
    col_map = {c.column_name: c.id for c in columns}

    imported = 0
    errors = []

    for idx, row in enumerate(rows):
        try:
            product = Product(
                template_id=active_template.id,
                created_by=current_user.id,
                status="pending"
            )
            db.add(product)
            db.flush()

            for col_name, value in row.items():
                if col_name in col_map and value:
                    pv = ProductValue(product_id=product.id, column_id=col_map[col_name], value=value)
                    db.add(pv)

            imported += 1
        except Exception as e:
            errors.append(f"Linha {idx + 2}: {str(e)}")

    db.commit()
    return BulkImportResponse(imported=imported, errors=errors)
