from utils.db import get_db_connection, get_db_cursor
from utils.security import hash_password, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)


def create_user(email: str, password: str, first_name: str = None, last_name: str = None) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return None
        pw_hash = hash_password(password)
        cur.execute(
            "INSERT INTO users (email, password_hash, first_name, last_name) VALUES (%s,%s,%s,%s) RETURNING id, email, first_name, last_name",
            (email, pw_hash, first_name, last_name)
        )
        return cur.fetchone()


def authenticate_user(email: str, password: str) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute("SELECT id, email, password_hash, first_name, last_name FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        if not user or not verify_password(password, user['password_hash']):
            return None
        token = create_access_token(user['id'], user['email'])
        return {"token": token, "user": user}


def get_user_by_id(user_id: int) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute("SELECT id, email, first_name, last_name FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()
