from fastapi import APIRouter, Depends, BackgroundTasks
from models.notification_models import NotificationBase, NotificationResponse, UpdateNotificationRequest
from controllers.notifications import create_notification_controller
from utils.security import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.notification_service import list_notifications, update_notification_db, delete_notification_db, bulk_save_notifications_db

router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return decode_token(credentials.credentials)


@router.get('/notifications', response_model=list[NotificationResponse])
def list_notifications(current_user=Depends(get_current_user)):
    rows = list_notifications(current_user['userId'])
    return [NotificationResponse(**r) for r in rows]


@router.post('/notifications', response_model=NotificationResponse)
def create_notification(notification: NotificationBase, background_tasks: BackgroundTasks, current_user=Depends(get_current_user)):
    return create_notification_controller(notification.dict(), current_user, background_tasks)


@router.put('/notifications/{notification_id}', response_model=NotificationResponse)
def update_notification(notification_id: str, request: UpdateNotificationRequest, current_user=Depends(get_current_user)):
    updated = update_notification_db(notification_id, request.dict(), current_user['userId'])
    if not updated:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse(**updated)


@router.delete('/notifications/{notification_id}')
def delete_notification(notification_id: str, current_user=Depends(get_current_user)):
    deleted = delete_notification_db(notification_id, current_user['userId'])
    if not deleted:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}


@router.put('/notifications')
def bulk_save_notifications(notifications: list[NotificationBase], current_user=Depends(get_current_user)):
    bulk_save_notifications_db([n.dict() for n in notifications], current_user['userId'])
    return {"message": "Notifications saved successfully"}
