-- =========================================
-- 01_init.sql
-- 목적: scmcore 데이터베이스 생성
-- 실행 순서: Docker MySQL 기동 후 가장 먼저 1번만 실행
-- =========================================

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS scmcore
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 사용 예: mysql -u root -p < db/01_init.sql
-- 또는 Docker: docker exec -i scmcore-mysql mysql -u root -p12345 < db/01_init.sql
