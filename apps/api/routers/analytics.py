# apps/api/routers/analytics.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.core.errors import log_and_classify
from apps.api.services.analytics_service import fetch_trends, fetch_breakdown

router = APIRouter(tags=["Analytics"])


@router.get("/analytics/trends")
def trends(
    metric: str = Query("revenue", pattern="^(revenue|orders|late_rate)$"),
    days: int = Query(180, ge=7, le=3650),
    db: Session = Depends(get_db),
):
    try:
        return fetch_trends(db, metric=metric, days=days)
    except Exception as e:
        error_type, message = log_and_classify(e, "Analytics /analytics/trends")
        return JSONResponse(
            status_code=503,
            content={"detail": message, "error_type": error_type},
        )


@router.get("/analytics/breakdown")
def breakdown(
    by: str = Query("region", pattern="^(category|department|region|shipping_mode)$"),
    days: int = Query(90, ge=7, le=3650),
    metric: str = Query("revenue", pattern="^(revenue|orders|late_rate)$"),
    db: Session = Depends(get_db),
):
    try:
        return fetch_breakdown(db, by=by, metric=metric, days=days)
    except Exception as e:
        error_type, message = log_and_classify(e, "Analytics /analytics/breakdown")
        return JSONResponse(
            status_code=503,
            content={"detail": message, "error_type": error_type},
        )
