# SCM Forecast & Inventory Copilot

AI 수요예측 + 재주문 추천 SCM (Forecast & Replenishment + Copilot)

## 구조
- **apps/api** — FastAPI (KPI, Forecast, Policy, Copilot)
- **apps/web** — React + Vite + TS (Home, Forecast, Inventory Policy, Copilot)
- **data/** — raw / staging / models (커밋 제외)
- **db/** — MySQL 스키마
- **mapping/** — DataCo 컬럼 매핑

## 실행
```bash
# MySQL (Docker)
docker compose up -d mysql

# DB·스키마·CSV 적재 후 (자세한 순서는 docs/SETUP_PROCESS_KR.md 참고)

# 백엔드
pip install -r apps/api/requirements.txt
# 방법 1 (권장): 프로젝트 루트에서
python apps/api/run.py
# 방법 2: apps/api 폴더에서
cd apps/api && uvicorn app.main:app --reload --port 8000

# 프론트 (다른 터미널)
cd apps/web && npm i && npm run dev

# Docker로 전체 스택 (MySQL + API + Web)
docker compose up -d --build
```

## 데이터
- DataCo Supply Chain Dataset (ZIP/CSV) → ETL 01~04 → MySQL + feature_daily_sku
