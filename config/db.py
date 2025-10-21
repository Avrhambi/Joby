"""Database initialization helpers kept under config as requested.
This module exposes init_db() which creates required tables/indexes if they
don't exist. It uses the shared utils.db connection helpers.
"""
from utils.db import get_db_connection, get_db_cursor
import logging

logger = logging.getLogger(__name__)


def init_db():
    """Create required tables and indexes if they do not exist."""
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Notifications table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id VARCHAR(50) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                seniority VARCHAR(50) NOT NULL,
                country VARCHAR(100) NOT NULL,
                location VARCHAR(100) NOT NULL,
                dist INTEGER DEFAULT 0,
                job_scope VARCHAR(50) NOT NULL,
                frequency VARCHAR(50) NOT NULL,
                email_enabled BOOLEAN DEFAULT true,
                last_sent_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_notifications_frequency ON notifications(frequency)")

    logger.info("Database initialized successfully (config.db.init_db)")
