# apps/api/core/errors.py
# Classify exceptions for clear API error responses and logging.
import logging

logger = logging.getLogger(__name__)

# Error types returned to frontend
ERROR_DATABASE_CONNECTION = "database_connection"
ERROR_TABLE_NOT_FOUND = "table_not_found"
ERROR_SCHEMA = "schema_error"
ERROR_DATA = "data_error"
ERROR_SERVER = "server_error"


def classify_error(e: Exception) -> tuple[str, str]:
    """
    Returns (error_type, human_message).
    error_type: for frontend to show specific UI message.
    human_message: short description for display/log.
    """
    err_msg = str(e).lower()
    exc_name = type(e).__name__.lower()

    # SQLAlchemy / DB-API
    if "operationalerror" in exc_name or "interfaceerror" in exc_name:
        return (
            ERROR_DATABASE_CONNECTION,
            "Database connection failed. Is MySQL running? Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD.",
        )
    if "can't connect" in err_msg or "connection refused" in err_msg or "unknown database" in err_msg:
        return (
            ERROR_DATABASE_CONNECTION,
            "Cannot connect to MySQL. Start MySQL (e.g. docker compose up -d mysql) and check .env.",
        )
    if "access denied" in err_msg:
        return (
            ERROR_DATABASE_CONNECTION,
            "Database access denied. Check DB_USER and DB_PASSWORD in .env.",
        )

    # Table / object does not exist
    if "programmingerror" in exc_name or "doesn't exist" in err_msg or ("table" in err_msg and "exist" in err_msg):
        return (
            ERROR_TABLE_NOT_FOUND,
            "Table or schema missing. Run db/01_init.sql and db/02_schema.sql, then load CSV.",
        )
    if "1146" in err_msg:  # MySQL table doesn't exist
        return (
            ERROR_TABLE_NOT_FOUND,
            "Table does not exist. Run db/02_schema.sql and scripts/load_dataco_csv.py.",
        )

    # Other SQL / data
    if "integrityerror" in exc_name or "dataerror" in exc_name:
        return (ERROR_DATA, f"Data or constraint error: {str(e)[:200]}")

    # Fallback
    return (ERROR_SERVER, str(e)[:300])


def log_and_classify(e: Exception, context: str = "") -> tuple[str, str]:
    """Log full traceback and return (error_type, human_message)."""
    logger.exception("%s: %s", context or "Error", e)
    return classify_error(e)
