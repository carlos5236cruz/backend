from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.category import Category, CategoryAttribute
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryAttributeCreate, CategoryAttributeResponse
)
from app.utils.security import require_admin, get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])


def _build_category_response(cat: Category, db: Session) -> dict:
    attrs = db.query(CategoryAttribute).filter(CategoryAttribute.category_id == cat.id).all()
    parent_name = None
    path = cat.name
    if cat.parent_id:
        parent = db.query(Category).filter(Category.id == cat.parent_id).first()
        if parent:
            parent_name = parent.name
            path = f"{parent.name}>>{cat.name}"
    return {
        "id": cat.id,
        "name": cat.name,
        "parent_id": cat.parent_id,
        "parent_name": parent_name,
        "path": path,
        "created_at": cat.created_at.isoformat() if cat.created_at else None,
        "attributes": [{"id": a.id, "attribute_name": a.attribute_name, "default_value": a.default_value} for a in attrs]
    }


@router.get("")
def list_categories(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cats = db.query(Category).order_by(Category.name).all()
    return [_build_category_response(c, db) for c in cats]


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cat = Category(name=data.name, parent_id=data.parent_id)
    db.add(cat)
    db.flush()

    if data.attributes:
        for attr in data.attributes:
            ca = CategoryAttribute(
                category_id=cat.id,
                attribute_name=attr.attribute_name,
                default_value=attr.default_value
            )
            db.add(ca)

    db.commit()
    db.refresh(cat)
    return _build_category_response(cat, db)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if data.name is not None:
        cat.name = data.name
    if data.parent_id is not None:
        cat.parent_id = data.parent_id

    db.commit()
    db.refresh(cat)
    return _build_category_response(cat, db)


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    db.delete(cat)
    db.commit()
    return {"message": "Categoria removida"}


@router.get("/{category_id}/attributes", response_model=List[CategoryAttributeResponse])
def get_attributes(category_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    attrs = db.query(CategoryAttribute).filter(CategoryAttribute.category_id == category_id).all()
    return [CategoryAttributeResponse.model_validate(a) for a in attrs]


@router.post("/{category_id}/attributes", response_model=CategoryAttributeResponse, status_code=201)
def create_attribute(
    category_id: int,
    data: CategoryAttributeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    attr = CategoryAttribute(
        category_id=category_id,
        attribute_name=data.attribute_name,
        default_value=data.default_value
    )
    db.add(attr)
    db.commit()
    db.refresh(attr)
    return CategoryAttributeResponse.model_validate(attr)


@router.delete("/{category_id}/attributes/{attr_id}")
def delete_attribute(category_id: int, attr_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    attr = db.query(CategoryAttribute).filter(
        CategoryAttribute.id == attr_id,
        CategoryAttribute.category_id == category_id
    ).first()
    if not attr:
        raise HTTPException(status_code=404, detail="Atributo não encontrado")
    db.delete(attr)
    db.commit()
    return {"message": "Atributo removido"}
