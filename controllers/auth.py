from services.user_service import create_user, authenticate_user
from models.user_models import SignupRequest, LoginRequest
from fastapi import HTTPException, status


def signup_controller(payload: SignupRequest):
    created = create_user(payload.email, payload.password, payload.firstName, payload.lastName)
    if not created:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = authenticate_user(payload.email, payload.password)
    return {"token": token['token'], "user": created}


def login_controller(payload: LoginRequest):
    auth = authenticate_user(payload.email, payload.password)
    if not auth:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": auth['token'], "user": auth['user']}
