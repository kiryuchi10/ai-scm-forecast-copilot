# apps/api/routers/kpi.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.core.errors import log_and_classify
from apps.api.services.kpi_service import fetch_kpi_summary

router = APIRouter(tags=["KPI"])


@router.get("/kpi/summary")
def kpi_summary(db: Session = Depends(get_db)):
    """실데이터만: total_revenue, total_orders, late_rate, top_products, top_late_orders, last_updated."""
    try:
        return fetch_kpi_summary(db)
    except Exception as e:
        error_type, message = log_and_classify(e, "KPI /kpi/summary")
        return JSONResponse(
            status_code=503,
            content={"detail": message, "error_type": error_type},
        )
