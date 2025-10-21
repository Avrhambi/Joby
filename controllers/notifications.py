from services.notification_service import create_notification_db, delayed_fetch_and_email
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


def create_notification_controller(notification: dict, current_user: dict, background_tasks):
    created = create_notification_db(notification, current_user['userId'])
    if not created:
        raise HTTPException(status_code=500, detail="Failed to create notification")

    # schedule initial email send
    try:
        background_tasks.add_task(delayed_fetch_and_email, user_email=created.get('email', current_user.get('email')), user_name=created.get('first_name', ''), notification=created)
    except Exception as e:
        logger.error(f"Failed to schedule initial notification send: {e}")

    return created
