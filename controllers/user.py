from services.user_service import get_user_by_id
from fastapi import HTTPException


def get_profile_controller(current_user: dict):
    user = get_user_by_id(current_user['userId'])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
