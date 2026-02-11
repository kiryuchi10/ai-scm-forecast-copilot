# apps/api/services/admin_service.py
# GET /api/admin/summary — 사용자 수·서버 상태·DB 상태·감사 이벤트 (테이블 없으면 안전한 기본값)
from sqlalchemy.orm import Session
from sqlalchemy import text


def fetch_admin_summary(db: Session) -> dict:
    user_count = 0
    try:
        r = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'users'")).scalar()
        if r and r > 0:
            user_count = int(db.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0)
    except Exception:
        pass

    db_status = "unknown"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = str(e)[:80]

    return {
        "user_count": user_count,
        "server_status": "ok",
        "db_status": db_status,
        "audit_events": 0,
    }
