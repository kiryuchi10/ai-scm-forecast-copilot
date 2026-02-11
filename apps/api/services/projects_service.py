# apps/api/services/projects_service.py
# 실데이터만. 스키마: etl_job_log(started_at, finished_at), ml_forecast_run(created_at, updated_at),
# ml_inventory_policy_result(as_of_dt, product_id, policy_key, run_id 없음)
from sqlalchemy.orm import Session
from sqlalchemy import text


def fetch_runs(db: Session, limit: int = 50) -> dict:
    # ETL: job_name, status, started_at, finished_at, message (row_count 없음)
    etl = []
    try:
        q_etl = text("""
            SELECT job_name, status, started_at, finished_at, message
            FROM etl_job_log
            ORDER BY started_at DESC
            LIMIT :limit
        """)
        for r in db.execute(q_etl, {"limit": limit}).fetchall():
            etl.append({
                "job_name": r.job_name,
                "status": r.status,
                "started_at": str(r.started_at) if r.started_at else None,
                "ended_at": str(r.finished_at) if r.finished_at else None,
                "row_count": None,
                "message": r.message,
            })
    except Exception:
        etl = []

    # Forecast: run_key, model_name, status, created_at, updated_at, metrics_json
    forecast = []
    try:
        q_forecast = text("""
            SELECT id, run_key, model_name, status, created_at, updated_at, metrics_json
            FROM ml_forecast_run
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        for r in db.execute(q_forecast, {"limit": limit}).fetchall():
            forecast.append({
                "run_id": r.run_key,
                "model_name": r.model_name,
                "status": r.status,
                "started_at": str(r.created_at) if r.created_at else None,
                "ended_at": str(r.updated_at) if r.updated_at else None,
                "metrics_json": r.metrics_json,
            })
    except Exception:
        forecast = []

    # Policy: policy_key, product_id, as_of_dt, reorder_point, safety_stock, recommended_qty, created_at (run_id 없음)
    policy = []
    try:
        q_policy = text("""
            SELECT p.policy_key, dp.product_key, p.as_of_dt, p.reorder_point, p.safety_stock, p.recommended_qty, p.created_at
            FROM ml_inventory_policy_result p
            JOIN dim_product dp ON dp.id = p.product_id
            ORDER BY p.created_at DESC
            LIMIT :limit
        """)
        for r in db.execute(q_policy, {"limit": limit}).fetchall():
            policy.append({
                "run_id": r.policy_key,
                "product_key": r.product_key,
                "as_of": str(r.as_of_dt) if r.as_of_dt else None,
                "reorder_point": float(r.reorder_point) if r.reorder_point is not None else None,
                "safety_stock": float(r.safety_stock) if r.safety_stock is not None else None,
                "recommended_qty": float(r.recommended_qty) if r.recommended_qty is not None else None,
                "created_at": str(r.created_at) if r.created_at else None,
            })
    except Exception:
        policy = []

    return {"etl": etl, "forecast": forecast, "policy": policy}
