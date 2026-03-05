from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.template import Template, TemplateColumn
from app.schemas.template import TemplateResponse, TemplateColumnResponse, TemplateUploadResponse
from app.utils.security import require_admin
from app.utils.excel import read_excel_columns

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.post("/upload", response_model=TemplateUploadResponse)
async def upload_template(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Apenas arquivos Excel (.xlsx, .xls) são aceitos")

    file_bytes = await file.read()
    try:
        columns = read_excel_columns(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler planilha: {str(e)}")

    if not columns:
        raise HTTPException(status_code=400, detail="Nenhuma coluna encontrada na planilha")

    template = Template(
        name=file.filename.rsplit(".", 1)[0],
        original_filename=file.filename,
        is_active=False,
        uploaded_by=current_user.id
    )
    db.add(template)
    db.flush()

    for order, col_name in enumerate(columns):
        tc = TemplateColumn(
            template_id=template.id,
            column_name=col_name,
            column_order=order
        )
        db.add(tc)

    db.commit()
    db.refresh(template)

    template_cols = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == template.id
    ).order_by(TemplateColumn.column_order).all()

    return TemplateUploadResponse(
        template=TemplateResponse(
            id=template.id,
            name=template.name,
            original_filename=template.original_filename,
            is_active=template.is_active,
            uploaded_by=template.uploaded_by,
            created_at=template.created_at,
            columns=[TemplateColumnResponse.model_validate(c) for c in template_cols]
        ),
        columns_detected=len(columns)
    )


@router.get("", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    templates = db.query(Template).order_by(Template.created_at.desc()).all()
    result = []
    for t in templates:
        cols = db.query(TemplateColumn).filter(
            TemplateColumn.template_id == t.id
        ).order_by(TemplateColumn.column_order).all()
        result.append(TemplateResponse(
            id=t.id, name=t.name, original_filename=t.original_filename,
            is_active=t.is_active, uploaded_by=t.uploaded_by, created_at=t.created_at,
            columns=[TemplateColumnResponse.model_validate(c) for c in cols]
        ))
    return result


@router.put("/{template_id}/activate")
def activate_template(template_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template não encontrado")

    db.query(Template).update({Template.is_active: False})
    template.is_active = True
    db.commit()
    return {"message": "Template ativado com sucesso"}


@router.get("/active", response_model=TemplateResponse)
def get_active_template(db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.is_active == True).first()
    if not template:
        raise HTTPException(status_code=404, detail="Nenhum template ativo")
    cols = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == template.id
    ).order_by(TemplateColumn.column_order).all()
    return TemplateResponse(
        id=template.id, name=template.name, original_filename=template.original_filename,
        is_active=template.is_active, uploaded_by=template.uploaded_by, created_at=template.created_at,
        columns=[TemplateColumnResponse.model_validate(c) for c in cols]
    )


@router.get("/{template_id}/columns", response_model=List[TemplateColumnResponse])
def get_template_columns(template_id: int, db: Session = Depends(get_db)):
    cols = db.query(TemplateColumn).filter(
        TemplateColumn.template_id == template_id
    ).order_by(TemplateColumn.column_order).all()
    return [TemplateColumnResponse.model_validate(c) for c in cols]
