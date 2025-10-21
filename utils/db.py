import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config.settings import DB_CONFIG
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def get_db_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)
