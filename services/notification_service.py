from utils.db import get_db_connection, get_db_cursor
from utils.email import send_job_email
from config.settings import JOBS_SERVER_URL
import requests
import logging

logger = logging.getLogger(__name__)


def create_notification_db(notification: dict, user_id: int) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute(
            "INSERT INTO notifications (id, user_id, title, seniority, country, location, dist, job_scope, frequency, email_enabled) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id, title, seniority, country, location, dist, job_scope, frequency, email_enabled, created_at",
            (
                notification['id'], user_id, notification['title'], notification['seniority'],
                notification['country'], notification['location'], notification['dist'],
                notification['job_scope'], notification['frequency'], notification['email_enabled']
            )
        )
        return cur.fetchone()


def list_notifications(user_id: int) -> list:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute(
            "SELECT id, title, seniority, country, location, dist, job_scope, frequency, email_enabled, last_sent_at, created_at, updated_at FROM notifications WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        return cur.fetchall()


def update_notification_db(notification_id: str, payload: dict, user_id: int) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute(
            "UPDATE notifications SET title=%s, seniority=%s, country=%s, location=%s, dist=%s, job_scope=%s, frequency=%s, email_enabled=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s AND user_id=%s RETURNING id, title, seniority, country, location, dist, job_scope, frequency, email_enabled, last_sent_at, created_at, updated_at",
            (
                payload.get('title'), payload.get('seniority'), payload.get('country'), payload.get('location'),
                payload.get('dist'), payload.get('job_scope'), payload.get('frequency'), payload.get('email_enabled'),
                notification_id, user_id
            )
        )
        return cur.fetchone()


def delete_notification_db(notification_id: str, user_id: int) -> dict:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute("DELETE FROM notifications WHERE id=%s AND user_id=%s RETURNING id", (notification_id, user_id))
        return cur.fetchone()


def bulk_save_notifications_db(notifications: list, user_id: int) -> None:
    with get_db_connection() as conn:
        cur = get_db_cursor(conn)
        cur.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        for notif in notifications:
            cur.execute("INSERT INTO notifications (id, user_id, title, seniority, country, location, dist, job_scope, frequency, email_enabled) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
                notif.get('id'), user_id, notif.get('title'), notif.get('seniority'), notif.get('country'), notif.get('location'), notif.get('dist'), notif.get('job_scope'), notif.get('frequency'), notif.get('email_enabled')
            ))
        return


def fetch_jobs_from_server(notification: dict) -> list:
    days_back_map = {"daily": 1, "twice_week": 3, "weekly": 7}
    job_scope_map = {"full time": "fulltime", "fulltime": "fulltime", "part time": "parttime", "parttime": "parttime", "temporary": "temporary"}
    payload = {
        "title": notification['title'],
        "seniority": notification['seniority'],
        "country": notification['country'],
        "location": notification['location'],
        "dist": int(notification.get('dist', 0)),
        "job_scope": job_scope_map.get(notification.get('job_scope', '').lower(), "fulltime"),
        "days_back": days_back_map.get(notification.get('frequency'), 1)
    }
    try:
        resp = requests.post(f"{JOBS_SERVER_URL}/jobs_search", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get('jobs', [])
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        return []


def delayed_fetch_and_email(user_email: str, user_name: str, notification: dict):
    import time
    max_wait_time = 600
    start = time.time()
    jobs = []
    while time.time() - start < max_wait_time:
        jobs = fetch_jobs_from_server(notification)
        if jobs:
            break
        time.sleep(30)

    if jobs:
        send_job_email(user_email, user_name, notification, jobs)
        with get_db_connection() as conn:
            cur = get_db_cursor(conn)
            cur.execute("UPDATE notifications SET last_sent_at = CURRENT_TIMESTAMP WHERE id = %s", (notification['id'],))
    else:
        logger.warning(f"No jobs found for {notification['title']} within timeout window")
