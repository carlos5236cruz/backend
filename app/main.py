from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.template import Template, TemplateColumn
from app.models.product import Product, ProductValue, ExportLog
from app.models.category import Category, CategoryAttribute
from app.utils.security import hash_password
from app.routers import auth, users, templates, products, categories, export, dashboard
import traceback

settings = get_settings()

app = FastAPI(
    title="Bling Product Manager API",
    description="Sistema para organizar, editar e exportar produtos para o Bling",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://atbeaauty.com.br",
        "https://atbeaauty.com.br",
        "http://www.atbeaauty.com.br",
        "https://www.atbeaauty.com.br",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = str(exc)
    tb = traceback.format_exc()
    print(f"ERROR on {request.url}: {error_detail}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(templates.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(export.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            admin = db.query(User).filter(User.email == "admin@bling.com").first()
            if not admin:
                admin = User(
                    name="Administrador",
                    email="admin@bling.com",
                    password_hash=hash_password("admin123"),
                    role="admin"
                )
                db.add(admin)
            else:
                admin.password_hash = hash_password("admin123")

            prod_admin = db.query(User).filter(User.email == "atbeaauty@gmail.com").first()
            if not prod_admin:
                prod_admin = User(
                    name="ATB Beauty",
                    email="atbeaauty@gmail.com",
                    password_hash=hash_password("Atbeaauty1!"),
                    role="admin"
                )
                db.add(prod_admin)
            else:
                prod_admin.password_hash = hash_password("Atbeaauty1!")

            db.commit()
        finally:
            db.close()
    except Exception as e:
        print(f"STARTUP DB ERROR: {e}")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/health/db")
def health_db():
    from sqlalchemy import text as sa_text
    try:
        db = SessionLocal()
        db.execute(sa_text("SELECT 1"))
        user_count = db.execute(sa_text("SELECT COUNT(*) FROM users")).scalar()
        db.close()
        return {"db": "connected", "users": user_count, "url": settings.DATABASE_URL[:30] + "..."}
    except Exception as e:
        return {"db": "error", "detail": str(e)}

