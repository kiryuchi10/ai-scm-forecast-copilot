# apps/api/main.py
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.core.config import settings
from apps.api.routers.kpi import router as kpi_router
from apps.api.routers.analytics import router as analytics_router
from apps.api.routers.projects import router as projects_router
from apps.api.routers.admin import router as admin_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SCM Copilot API",
    version="0.1.0",
)


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """500 발생 시 로그에 traceback 출력 + 응답에 메시지 포함 (원인 파악용)."""
    tb = traceback.format_exc()
    logger.error("Unhandled exception: %s\n%s", exc, tb)
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__,
        },
    )


origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kpi_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    """DB 연결 및 테이블 존재 여부 확인 (500 원인 파악용)."""
    from apps.api.core.database import SessionLocal
    from sqlalchemy import text
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        has_table = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'fact_order_item'")).scalar() > 0
        return {"status": "ok", "db": "connected", "fact_order_item_exists": bool(has_table)}
    except Exception as e:
        logger.exception("health_db failed")
        return JSONResponse(status_code=503, content={"status": "error", "db": str(e)})
    finally:
        db.close()
