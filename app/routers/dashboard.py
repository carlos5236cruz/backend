from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.template import Template
from app.models.product import Product
from app.models.category import Category
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    active_template = db.query(Template).filter(Template.is_active == True).first()
    template_id = active_template.id if active_template else 0

    total_products = db.query(func.count(Product.id)).filter(
        Product.template_id == template_id
    ).scalar() or 0

    pending = db.query(func.count(Product.id)).filter(
        Product.template_id == template_id,
        Product.status == "pending"
    ).scalar() or 0

    reviewed = db.query(func.count(Product.id)).filter(
        Product.template_id == template_id,
        Product.status == "reviewed"
    ).scalar() or 0

    total_categories = db.query(func.count(Category.id)).scalar() or 0

    recent_products = db.query(Product).filter(
        Product.template_id == template_id
    ).order_by(Product.updated_at.desc()).limit(5).all()

    return {
        "total_products": total_products,
        "pending": pending,
        "reviewed": reviewed,
        "total_categories": total_categories,
        "active_template": active_template.name if active_template else None,
        "recent_updates": [{
            "id": p.id,
            "status": p.status,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None
        } for p in recent_products]
    }
