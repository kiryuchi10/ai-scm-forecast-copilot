# apps/api/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from apps.api.core.config import settings


def make_mysql_url() -> str:
    user = settings.MYSQL_USER
    pwd = settings.MYSQL_PASSWORD
    host = settings.MYSQL_HOST
    port = settings.MYSQL_PORT
    db = settings.MYSQL_DB
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}?charset=utf8mb4"


engine = create_engine(
    make_mysql_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
