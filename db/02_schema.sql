-- =========================================
-- 02_schema.sql
-- 목적: SCM Core 정규화 테이블 생성 (DataCo CSV 적재용)
-- 실행 순서: 01_init.sql 실행 후 실행
-- =========================================

USE scmcore;
SET NAMES utf8mb4;

-- --------------------------
-- DIMENSION: 카테고리 / 부서 / 상품
-- --------------------------
CREATE TABLE IF NOT EXISTS dim_category (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  category_key  VARCHAR(64) NOT NULL UNIQUE,
  name          VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS dim_department (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  department_key  VARCHAR(64) NOT NULL UNIQUE,
  name            VARCHAR(255) NOT NULL,
  created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS dim_product (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  product_key      VARCHAR(64) NOT NULL UNIQUE,
  product_name     VARCHAR(512) NOT NULL,
  category_id      BIGINT NULL,
  department_id    BIGINT NULL,
  base_price       DOUBLE NULL,
  is_active        TINYINT(1) NOT NULL DEFAULT 1,
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_prod_category (category_id),
  INDEX idx_prod_department (department_id),
  CONSTRAINT fk_prod_category FOREIGN KEY (category_id) REFERENCES dim_category(id),
  CONSTRAINT fk_prod_department FOREIGN KEY (department_id) REFERENCES dim_department(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------
-- DIMENSION: 고객 (PII 제외)
-- --------------------------
CREATE TABLE IF NOT EXISTS dim_customer (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_key      VARCHAR(64) NOT NULL UNIQUE,
  segment           VARCHAR(64) NULL,
  market            VARCHAR(64) NULL,
  region            VARCHAR(64) NULL,
  country           VARCHAR(128) NULL,
  state             VARCHAR(128) NULL,
  city              VARCHAR(128) NULL,
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_cust_geo (country, state, city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------
-- FACT: 주문
-- --------------------------
CREATE TABLE IF NOT EXISTS fact_order (
  id               BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_key        VARCHAR(64) NOT NULL UNIQUE,
  order_date       DATETIME(6) NOT NULL,
  customer_id      BIGINT NULL,
  order_status     VARCHAR(64) NULL,
  order_region     VARCHAR(64) NULL,
  order_country    VARCHAR(128) NULL,
  order_state      VARCHAR(128) NULL,
  order_city       VARCHAR(128) NULL,
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_order_date (order_date),
  INDEX idx_order_customer (customer_id),
  CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fact_order_item (
  id                    BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_item_key        VARCHAR(64) NOT NULL UNIQUE,
  order_id              BIGINT NOT NULL,
  product_id            BIGINT NOT NULL,
  quantity              DOUBLE NOT NULL,
  unit_price            DOUBLE NULL,
  sales                 DOUBLE NULL,
  discount_rate         DOUBLE NULL,
  profit_per_order      DOUBLE NULL,
  profit_ratio          DOUBLE NULL,
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_item_order (order_id),
  INDEX idx_item_product (product_id),
  CONSTRAINT fk_item_order FOREIGN KEY (order_id) REFERENCES fact_order(id),
  CONSTRAINT fk_item_product FOREIGN KEY (product_id) REFERENCES dim_product(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS fact_shipping (
  id                         BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id                   BIGINT NOT NULL UNIQUE,
  shipping_mode              VARCHAR(64) NULL,
  delivery_status            VARCHAR(64) NULL,
  scheduled_days             DOUBLE NULL,
  real_shipping_days         DOUBLE NULL,
  delay_days                 DOUBLE NULL,
  late_delivery_risk         TINYINT(1) NULL,
  created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_ship_mode (shipping_mode),
  INDEX idx_ship_late (late_delivery_risk),
  CONSTRAINT fk_ship_order FOREIGN KEY (order_id) REFERENCES fact_order(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------
-- FEATURE: 일별 SKU 집계 (ML 입력)
-- --------------------------
CREATE TABLE IF NOT EXISTS feature_daily_sku (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  dt                 DATE NOT NULL,
  product_id         BIGINT NOT NULL,
  qty                DOUBLE NOT NULL DEFAULT 0,
  sales              DOUBLE NULL,
  avg_unit_price     DOUBLE NULL,
  discount_rate_avg  DOUBLE NULL,
  dow                TINYINT NULL,
  week_of_year       SMALLINT NULL,
  month              TINYINT NULL,
  lag_1              DOUBLE NULL,
  lag_7              DOUBLE NULL,
  roll_mean_7        DOUBLE NULL,
  roll_std_7         DOUBLE NULL,
  roll_mean_28       DOUBLE NULL,
  roll_std_28        DOUBLE NULL,
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_daily_sku (dt, product_id),
  INDEX idx_feat_dt (dt),
  INDEX idx_feat_product (product_id),
  CONSTRAINT fk_feat_product FOREIGN KEY (product_id) REFERENCES dim_product(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------
-- ML: 예측 실행 / 결과
-- --------------------------
CREATE TABLE IF NOT EXISTS ml_forecast_run (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  run_key            VARCHAR(64) NOT NULL UNIQUE,
  model_name         VARCHAR(64) NOT NULL,
  model_version      VARCHAR(64) NULL,
  train_start        DATE NULL,
  train_end          DATE NULL,
  horizon_days       INT NOT NULL DEFAULT 28,
  metrics_json       JSON NULL,
  status             VARCHAR(32) NOT NULL DEFAULT 'done',
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_run_model (model_name),
  INDEX idx_run_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ml_forecast_result (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  run_id             BIGINT NOT NULL,
  product_id         BIGINT NOT NULL,
  target_dt          DATE NOT NULL,
  yhat               DOUBLE NOT NULL,
  yhat_lo            DOUBLE NULL,
  yhat_hi            DOUBLE NULL,
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_run_prod_dt (run_id, product_id, target_dt),
  INDEX idx_fc_target (target_dt),
  INDEX idx_fc_product (product_id),
  CONSTRAINT fk_fc_run FOREIGN KEY (run_id) REFERENCES ml_forecast_run(id),
  CONSTRAINT fk_fc_product FOREIGN KEY (product_id) REFERENCES dim_product(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ml_inventory_policy_result (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  policy_key         VARCHAR(64) NOT NULL UNIQUE,
  as_of_dt           DATE NOT NULL,
  product_id         BIGINT NOT NULL,
  service_level      DOUBLE NOT NULL DEFAULT 0.95,
  lead_time_days     INT NOT NULL DEFAULT 14,
  on_hand            DOUBLE NOT NULL DEFAULT 0,
  demand_lt          DOUBLE NOT NULL DEFAULT 0,
  safety_stock       DOUBLE NOT NULL DEFAULT 0,
  reorder_point      DOUBLE NOT NULL DEFAULT 0,
  recommended_qty    DOUBLE NOT NULL DEFAULT 0,
  moq                DOUBLE NULL,
  explanation_json   JSON NULL,
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_policy_dt (as_of_dt),
  INDEX idx_policy_product (product_id),
  CONSTRAINT fk_policy_product FOREIGN KEY (product_id) REFERENCES dim_product(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------
-- ETL 로그
-- --------------------------
CREATE TABLE IF NOT EXISTS etl_upload_log (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  upload_key         VARCHAR(64) NOT NULL UNIQUE,
  filename           VARCHAR(512) NOT NULL,
  file_sha256        VARCHAR(128) NULL,
  status             VARCHAR(32) NOT NULL DEFAULT 'uploaded',
  message            TEXT NULL,
  created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_upload_status (status),
  INDEX idx_upload_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS etl_job_log (
  id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
  job_key            VARCHAR(64) NOT NULL UNIQUE,
  upload_id          BIGINT NULL,
  job_name           VARCHAR(128) NOT NULL,
  status             VARCHAR(32) NOT NULL DEFAULT 'running',
  started_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  finished_at        TIMESTAMP NULL,
  message            TEXT NULL,
  INDEX idx_job_name (job_name),
  INDEX idx_job_status (status),
  CONSTRAINT fk_job_upload FOREIGN KEY (upload_id) REFERENCES etl_upload_log(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
