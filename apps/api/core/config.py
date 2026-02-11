# apps/api/core/config.py
import os


class Settings:
    """DB/API 설정. 환경변수 MYSQL_* 또는 DB_* 지원 (로더·도커와 호환)."""
    MYSQL_HOST: str = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", "3306"))
    MYSQL_DB: str = os.getenv("MYSQL_DB") or os.getenv("DB_NAME", "scmcore")
    MYSQL_USER: str = os.getenv("MYSQL_USER") or os.getenv("DB_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASSWORD", "12345")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")


settings = Settings()
