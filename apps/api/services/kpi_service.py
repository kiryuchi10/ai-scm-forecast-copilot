# apps/api/services/kpi_service.py
# 실데이터만 사용. fact_order_item.order_id → fact_order.id, product_id → dim_product.id
# fact_shipping.order_id → fact_order.id (order_key는 fact_order에서 조회)
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def fetch_kpi_summary(db: Session) -> dict:
    # 1) total revenue (fact_order_item.sales)
    q_rev = text("""
        SELECT COALESCE(SUM(foi.sales), 0) AS total_revenue
        FROM fact_order_item foi
    """)
    total_revenue = float(db.execute(q_rev).scalar() or 0)

    # 2) total orders (fact_order)
    q_orders = text("""
        SELECT COUNT(DISTINCT fo.id) AS total_orders
        FROM fact_order fo
    """)
    total_orders = int(db.execute(q_orders).scalar() or 0)

    # 3) late rate (fact_shipping: late_delivery_risk 또는 delay_days > 0)
    try:
        q_late = text("""
            SELECT COALESCE(AVG(fs.late_delivery_risk), 0) AS late_rate
            FROM fact_shipping fs
        """)
        late_rate = float(db.execute(q_late).scalar() or 0)
    except Exception:
        q_late = text("""
            SELECT COALESCE(AVG(CASE WHEN fs.delay_days > 0 THEN 1 ELSE 0 END), 0) AS late_rate
            FROM fact_shipping fs
        """)
        late_rate = float(db.execute(q_late).scalar() or 0)

    # 4) top products by revenue (fact_order_item.product_id → dim_product.id)
    q_top_products = text("""
        SELECT
          dp.product_key AS product_key,
          dp.product_name AS product_name,
          COALESCE(SUM(foi.sales), 0) AS revenue,
          COALESCE(SUM(foi.quantity), 0) AS qty
        FROM fact_order_item foi
        JOIN dim_product dp ON dp.id = foi.product_id
        GROUP BY dp.id, dp.product_key, dp.product_name
        ORDER BY revenue DESC
        LIMIT 10
    """)
    rows = db.execute(q_top_products).fetchall()
    top_products = [
        {
            "product_key": r.product_key,
            "product_name": r.product_name or "",
            "revenue": float(r.revenue or 0),
            "qty": float(r.qty or 0),
        }
        for r in rows
    ]

    # 5) top late orders (fact_shipping.order_id → fact_order.id, order_key from fact_order)
    q_top_late = text("""
        SELECT
          fo.order_key AS order_key,
          COALESCE(fs.delay_days, 0) AS delay_days,
          fs.shipping_mode AS shipping_mode,
          fs.delivery_status AS delivery_status
        FROM fact_shipping fs
        JOIN fact_order fo ON fo.id = fs.order_id
        ORDER BY fs.delay_days DESC
        LIMIT 10
    """)
    rows = db.execute(q_top_late).fetchall()
    top_late_orders = [
        {
            "order_key": r.order_key or "",
            "delay_days": float(r.delay_days or 0),
            "shipping_mode": r.shipping_mode or "",
            "delivery_status": r.delivery_status or "",
        }
        for r in rows
    ]

    # 6) last_updated: 최신 주문일
    try:
        q_last = text("SELECT MAX(fo.order_date) FROM fact_order fo")
        last_dt = db.execute(q_last).scalar()
        last_updated = str(last_dt) if last_dt else datetime.utcnow().isoformat()
    except Exception:
        last_updated = datetime.utcnow().isoformat()

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "late_rate": late_rate,
        "top_products": top_products,
        "top_late_orders": top_late_orders,
        "last_updated": last_updated,
    }
