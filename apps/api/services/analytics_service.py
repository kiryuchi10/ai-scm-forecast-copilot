# apps/api/services/analytics_service.py
# 실데이터만. fact_order.order_date 기준 기간 필터, fact_order_item.order_id → fact_order.id
# fact_shipping.order_id → fact_order.id (날짜는 order_date 사용)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text


def _since(days: int) -> str:
    dt = datetime.utcnow() - timedelta(days=days)
    return dt.strftime("%Y-%m-%d")


def fetch_trends(db: Session, metric: str, days: int) -> dict:
    since = _since(days)

    if metric == "revenue":
        q = text("""
            SELECT DATE(fo.order_date) AS dt, COALESCE(SUM(foi.sales), 0) AS value
            FROM fact_order fo
            JOIN fact_order_item foi ON foi.order_id = fo.id
            WHERE fo.order_date >= :since
            GROUP BY DATE(fo.order_date)
            ORDER BY dt ASC
        """)
    elif metric == "orders":
        q = text("""
            SELECT DATE(fo.order_date) AS dt, COUNT(DISTINCT fo.id) AS value
            FROM fact_order fo
            WHERE fo.order_date >= :since
            GROUP BY DATE(fo.order_date)
            ORDER BY dt ASC
        """)
    else:
        # late_rate by day (order_date 기준, fact_shipping join)
        q = text("""
            SELECT DATE(fo.order_date) AS dt,
                   COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS value
            FROM fact_order fo
            JOIN fact_shipping fs ON fs.order_id = fo.id
            WHERE fo.order_date >= :since
            GROUP BY DATE(fo.order_date)
            ORDER BY dt ASC
        """)

    rows = db.execute(q, {"since": since}).fetchall()
    return {
        "metric": metric,
        "days": days,
        "series": [{"dt": str(r.dt), "value": float(r.value)} for r in rows],
    }


def fetch_breakdown(db: Session, by: str, metric: str, days: int) -> dict:
    since = _since(days)

    if by == "region":
        if metric == "revenue":
            q = text(f"""
                SELECT fo.order_region AS `key`, COALESCE(SUM(foi.sales), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY fo.order_region
                ORDER BY value DESC
                LIMIT 50
            """)
        elif metric == "orders":
            q = text("""
                SELECT fo.order_region AS `key`, COUNT(DISTINCT fo.id) AS value
                FROM fact_order fo
                WHERE fo.order_date >= :since
                GROUP BY fo.order_region
                ORDER BY value DESC
                LIMIT 50
            """)
        else:
            q = text("""
                SELECT fo.order_region AS `key`,
                       COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS value
                FROM fact_order fo
                JOIN fact_shipping fs ON fs.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY fo.order_region
                ORDER BY value DESC
                LIMIT 50
            """)
    elif by == "category":
        if metric == "revenue":
            q = text("""
                SELECT COALESCE(dc.name, CAST(dp.category_id AS CHAR)) AS `key`,
                       COALESCE(SUM(foi.sales), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_category dc ON dc.id = dp.category_id
                WHERE fo.order_date >= :since
                GROUP BY dp.category_id, dc.name
                ORDER BY value DESC
                LIMIT 50
            """)
        elif metric == "orders":
            q = text("""
                SELECT COALESCE(dc.name, CAST(dp.category_id AS CHAR)) AS `key`,
                       COUNT(DISTINCT fo.id) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_category dc ON dc.id = dp.category_id
                WHERE fo.order_date >= :since
                GROUP BY dp.category_id, dc.name
                ORDER BY value DESC
                LIMIT 50
            """)
        else:
            q = text("""
                SELECT COALESCE(dc.name, CAST(dp.category_id AS CHAR)) AS `key`,
                       COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_category dc ON dc.id = dp.category_id
                JOIN fact_shipping fs ON fs.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY dp.category_id, dc.name
                ORDER BY value DESC
                LIMIT 50
            """)
    elif by == "department":
        if metric == "revenue":
            q = text("""
                SELECT COALESCE(dd.name, CAST(dp.department_id AS CHAR)) AS `key`,
                       COALESCE(SUM(foi.sales), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_department dd ON dd.id = dp.department_id
                WHERE fo.order_date >= :since
                GROUP BY dp.department_id, dd.name
                ORDER BY value DESC
                LIMIT 50
            """)
        elif metric == "orders":
            q = text("""
                SELECT COALESCE(dd.name, CAST(dp.department_id AS CHAR)) AS `key`,
                       COUNT(DISTINCT fo.id) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_department dd ON dd.id = dp.department_id
                WHERE fo.order_date >= :since
                GROUP BY dp.department_id, dd.name
                ORDER BY value DESC
                LIMIT 50
            """)
        else:
            q = text("""
                SELECT COALESCE(dd.name, CAST(dp.department_id AS CHAR)) AS `key`,
                       COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN dim_product dp ON dp.id = foi.product_id
                LEFT JOIN dim_department dd ON dd.id = dp.department_id
                JOIN fact_shipping fs ON fs.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY dp.department_id, dd.name
                ORDER BY value DESC
                LIMIT 50
            """)
    else:
        # shipping_mode
        if metric == "late_rate":
            q = text("""
                SELECT fs.shipping_mode AS `key`,
                       COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS value
                FROM fact_shipping fs
                JOIN fact_order fo ON fo.id = fs.order_id
                WHERE fo.order_date >= :since
                GROUP BY fs.shipping_mode
                ORDER BY value DESC
                LIMIT 50
            """)
        elif metric == "revenue":
            q = text("""
                SELECT fs.shipping_mode AS `key`, COALESCE(SUM(foi.sales), 0) AS value
                FROM fact_order fo
                JOIN fact_order_item foi ON foi.order_id = fo.id
                JOIN fact_shipping fs ON fs.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY fs.shipping_mode
                ORDER BY value DESC
                LIMIT 50
            """)
        else:
            q = text("""
                SELECT fs.shipping_mode AS `key`, COUNT(DISTINCT fo.id) AS value
                FROM fact_order fo
                JOIN fact_shipping fs ON fs.order_id = fo.id
                WHERE fo.order_date >= :since
                GROUP BY fs.shipping_mode
                ORDER BY value DESC
                LIMIT 50
            """)

    rows = db.execute(q, {"since": since}).fetchall()
    return {
        "by": by,
        "metric": metric,
        "days": days,
        "items": [{"key": str(r.key) if r.key is not None else "", "value": float(r.value)} for r in rows],
    }
