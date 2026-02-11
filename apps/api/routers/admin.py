# apps/api/routers/admin.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.services.admin_service import fetch_admin_summary

router = APIRouter(tags=["Admin"])


@router.get("/admin/summary")
def admin_summary(db: Session = Depends(get_db)):
    """사용자 수, 서버 상태, DB 상태, 감사 이벤트. 예외 시에도 500 없이 안전한 값 반환."""
    try:
        return fetch_admin_summary(db)
    except Exception as e:
        return {
            "user_count": 0,
            "server_status": "ok",
            "db_status": str(e)[:120],
            "audit_events": 0,
        }
