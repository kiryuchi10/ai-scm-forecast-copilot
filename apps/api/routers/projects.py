# apps/api/routers/projects.py
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.api.core.database import get_db
from apps.api.core.errors import log_and_classify
from apps.api.services.projects_service import fetch_runs

router = APIRouter(tags=["Projects"])


@router.get("/projects/runs")
def runs(limit: int = Query(50, ge=1, le=200), db: Session = Depends(get_db)):
    """실데이터만: etl_job_log, ml_forecast_run, ml_inventory_policy_result 최근 실행 목록."""
    try:
        return fetch_runs(db, limit=limit)
    except Exception as e:
        error_type, message = log_and_classify(e, "Projects /projects/runs")
        return JSONResponse(
            status_code=503,
            content={"detail": message, "error_type": error_type},
        )
