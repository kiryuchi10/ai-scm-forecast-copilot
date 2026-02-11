-- =========================================
-- 001: 데이터베이스 생성 (SCM Core)
-- Docker MySQL 컨테이너는 MYSQL_DATABASE로 이미 생성할 수 있으나,
-- 수동 실행 시를 위해 CREATE DATABASE 명시
-- =========================================
SET NAMES utf8mb4;
SET character_set_client = utf8mb4;

CREATE DATABASE IF NOT EXISTS scmcore
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- 사용할 DB 지정 (이후 002_schema.sql에서 테이블이 이 DB에 생성됨)
USE scmcore;
