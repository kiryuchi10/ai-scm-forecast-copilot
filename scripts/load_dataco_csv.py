#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
목적: DataCoSupplyChainDataset.csv를 MySQL scmcore DB에 적재
사용: python scripts/load_dataco_csv.py
필요: pip install pandas pymysql
환경변수: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CSV_PATH
기본값: localhost, 3306, scmcore, scmcore12345, scmcore, data/raw/DataCoSupplyChainDataset.csv
"""

import os
import sys
from datetime import datetime

try:
    import pandas as pd
    import pymysql
except ImportError:
    print("필요 패키지: pip install pandas pymysql")
    sys.exit(1)

# DB 설정 (환경변수 또는 기본값)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "scmcore")
DB_PASSWORD = os.getenv("DB_PASSWORD", "scmcore12345")
DB_NAME = os.getenv("DB_NAME", "scmcore")
CSV_PATH = os.getenv("CSV_PATH", "data/raw/DataCoSupplyChainDataset.csv")
# CSV 샘플만 적재 (0이면 전체)
MAX_ROWS = int(os.getenv("MAX_ROWS", "0"))


def normalize_col(df):
    """컬럼명 공백/괄호 정리 → 소문자_스네이크"""
    def n(c):
        c = c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
        return c
    df.columns = [n(c) for c in df.columns]
    return df


def parse_date(s):
    """날짜 파싱 (예: 1/31/2018 22:56)"""
    if pd.isna(s):
        return None
    try:
        return pd.to_datetime(s)
    except Exception:
        return None


def main():
    if not os.path.isfile(CSV_PATH):
        print(f"CSV 파일 없음: {CSV_PATH}")
        sys.exit(1)

    print("CSV 읽는 중...")
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8", nrows=MAX_ROWS if MAX_ROWS else None)
    except UnicodeDecodeError:
        df = pd.read_csv(CSV_PATH, encoding="latin1", nrows=MAX_ROWS if MAX_ROWS else None)
    df = normalize_col(df)
    print(f"행 수: {len(df)}")

    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    try:
        with conn.cursor() as cur:
            # 컬럼 매핑 (DataCo 정규화 후: order date (DateOrders)→order_date_dateorders 등)
            order_date_col = next((c for c in df.columns if "order" in c and "date" in c), "order_date_dateorders")
            order_key_col = next((c for c in df.columns if c == "order_id" or "order_id" in c), "order_id")
            product_key_col = next((c for c in df.columns if "product_card" in c and "id" in c), "product_card_id")
            cat_key_col = next((c for c in df.columns if "category_id" in c and "product" not in c), "category_id")
            dept_key_col = next((c for c in df.columns if "department_id" in c), "department_id")

            # 1) dim_category
            if cat_key_col in df.columns and "category_name" in df.columns:
                cats = df[[cat_key_col, "category_name"]].drop_duplicates()
                for _, r in cats.iterrows():
                    cur.execute(
                        "INSERT IGNORE INTO dim_category (category_key, name) VALUES (%s, %s)",
                        (str(r[cat_key_col]), str(r["category_name"])[:255]),
                    )
            conn.commit()
            print("dim_category 적재 완료")

            # 2) dim_department
            if dept_key_col in df.columns and "department_name" in df.columns:
                depts = df[[dept_key_col, "department_name"]].drop_duplicates()
                for _, r in depts.iterrows():
                    cur.execute(
                        "INSERT IGNORE INTO dim_department (department_key, name) VALUES (%s, %s)",
                        (str(r[dept_key_col]), str(r["department_name"])[:255]),
                    )
            conn.commit()
            print("dim_department 적재 완료")

            # 3) dim_product (product_card_id, product_name, category_id, department_id, base_price)
            cur.execute("SELECT id, category_key FROM dim_category")
            cat_map = {r["category_key"]: r["id"] for r in cur.fetchall()}
            cur.execute("SELECT id, department_key FROM dim_department")
            dept_map = {r["department_key"]: r["id"] for r in cur.fetchall()}
            prods = df[[product_key_col, "product_name", cat_key_col, dept_key_col, "product_price"]].drop_duplicates(subset=[product_key_col])
            for _, r in prods.iterrows():
                cid = cat_map.get(str(r[cat_key_col]))
                did = dept_map.get(str(r[dept_key_col]))
                price = r.get("product_price")
                if pd.isna(price):
                    price = None
                cur.execute(
                    """INSERT IGNORE INTO dim_product (product_key, product_name, category_id, department_id, base_price)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (str(r[product_key_col]), str(r["product_name"])[:512], cid, did, price),
                )
            conn.commit()
            print("dim_product 적재 완료")

            # 4) dim_customer (customer_key = order_customer_id, segment, market, region, country, state, city)
            cust_key_col = next((c for c in df.columns if "order_customer_id" in c or (c == "customer_id")), "order_customer_id")
            if cust_key_col in df.columns:
                cust_cols = [cust_key_col] + [c for c in ["customer_segment", "market", "order_region", "order_country", "order_state", "order_city"] if c in df.columns]
                custs = df[cust_cols].drop_duplicates(subset=[cust_key_col])
                for _, r in custs.iterrows():
                    cur.execute(
                        """INSERT IGNORE INTO dim_customer (customer_key, segment, market, region, country, state, city)
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (
                            str(r[cust_key_col]),
                            str(r.get("customer_segment", ""))[:64] if pd.notna(r.get("customer_segment")) else None,
                            str(r.get("market", ""))[:64] if pd.notna(r.get("market")) else None,
                            str(r.get("order_region", ""))[:64] if pd.notna(r.get("order_region")) else None,
                            str(r.get("order_country", ""))[:128] if pd.notna(r.get("order_country")) else None,
                            str(r.get("order_state", ""))[:128] if pd.notna(r.get("order_state")) else None,
                            str(r.get("order_city", ""))[:128] if pd.notna(r.get("order_city")) else None,
                        ),
                    )
            conn.commit()
            print("dim_customer 적재 완료")

            # 5) fact_order
            cur.execute("SELECT id, product_key FROM dim_product")
            prod_map = {str(r["product_key"]): r["id"] for r in cur.fetchall()}
            cur.execute("SELECT id, customer_key FROM dim_customer")
            cust_id_map = {str(r["customer_key"]): r["id"] for r in cur.fetchall()}

            orders_done = set()
            for _, r in df.iterrows():
                ok = str(r[order_key_col])
                if ok in orders_done:
                    continue
                orders_done.add(ok)
                od = parse_date(r.get(order_date_col))
                if od is None:
                    od = datetime.now()
                cid = cust_id_map.get(str(r.get(cust_key_col, "")))
                cur.execute(
                    """INSERT IGNORE INTO fact_order (order_key, order_date, customer_id, order_status, order_region, order_country, order_state, order_city)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        ok,
                        od,
                        cid,
                        str(r.get("order_status", ""))[:64] if pd.notna(r.get("order_status")) else None,
                        str(r.get("order_region", ""))[:64] if pd.notna(r.get("order_region")) else None,
                        str(r.get("order_country", ""))[:128] if pd.notna(r.get("order_country")) else None,
                        str(r.get("order_state", ""))[:128] if pd.notna(r.get("order_state")) else None,
                        str(r.get("order_city", ""))[:128] if pd.notna(r.get("order_city")) else None,
                    ),
                )
            conn.commit()
            print("fact_order 적재 완료")

            # 6) order_id 매핑
            cur.execute("SELECT id, order_key FROM fact_order")
            order_id_map = {r["order_key"]: r["id"] for r in cur.fetchall()}

            # 7) fact_order_item
            item_key_col = [c for c in df.columns if "order_item_id" in c][0] if [c for c in df.columns if "order_item_id" in c] else "order_item_id"
            qty_col = [c for c in df.columns if "quantity" in c or "order_item_quantity" in c]
            qty_col = qty_col[0] if qty_col else "order_item_quantity"
            for _, r in df.iterrows():
                oid = order_id_map.get(str(r[order_key_col]))
                if oid is None:
                    continue
                pid = prod_map.get(str(r[product_key_col]))
                if pid is None:
                    continue
                item_key = str(r.get(item_key_col, ""))
                if not item_key:
                    continue
                qty = float(r.get(qty_col, 0) or 0)
                unit_price = r.get("order_item_product_price")
                unit_price = float(unit_price) if pd.notna(unit_price) else None
                sales = r.get("sales")
                sales = float(sales) if pd.notna(sales) else None
                disc = r.get("order_item_discount_rate")
                disc = float(disc) if pd.notna(disc) else None
                profit = r.get("order_profit_per_order")
                profit = float(profit) if pd.notna(profit) else None
                ratio = r.get("order_item_profit_ratio")
                ratio = float(ratio) if pd.notna(ratio) else None
                cur.execute(
                    """INSERT IGNORE INTO fact_order_item (order_item_key, order_id, product_id, quantity, unit_price, sales, discount_rate, profit_per_order, profit_ratio)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (item_key, oid, pid, qty, unit_price, sales, disc, profit, ratio),
                )
            conn.commit()
            print("fact_order_item 적재 완료")

            # 8) fact_shipping (order_id 1:1, 주문당 한 행만)
            ship_cols = [order_key_col] + [c for c in ["days_for_shipment_scheduled", "days_for_shipping_real", "late_delivery_risk", "shipping_mode", "delivery_status"] if c in df.columns]
            ships = df[ship_cols].drop_duplicates(subset=[order_key_col])
            for _, r in ships.iterrows():
                oid = order_id_map.get(str(r[order_key_col]))
                if oid is None:
                    continue
                sched = r.get("days_for_shipment_scheduled")
                real = r.get("days_for_shipping_real")
                sched = float(sched) if pd.notna(sched) else None
                real = float(real) if pd.notna(real) else None
                delay = (real - sched) if real is not None and sched is not None else None
                late = r.get("late_delivery_risk")
                late = int(late) if pd.notna(late) and str(late) in ("0", "1") else None
                cur.execute(
                    """INSERT IGNORE INTO fact_shipping (order_id, shipping_mode, delivery_status, scheduled_days, real_shipping_days, delay_days, late_delivery_risk)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        oid,
                        str(r.get("shipping_mode", ""))[:64] if pd.notna(r.get("shipping_mode")) else None,
                        str(r.get("delivery_status", ""))[:64] if pd.notna(r.get("delivery_status")) else None,
                        sched,
                        real,
                        delay,
                        late,
                    ),
                )
            conn.commit()
            print("fact_shipping 적재 완료")

    finally:
        conn.close()

    print("전체 CSV 적재 완료.")


if __name__ == "__main__":
    main()
