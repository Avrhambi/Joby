from fastapi import APIRouter
from models.user_models import SignupRequest, LoginRequest, TokenResponse
from controllers.auth import signup_controller, login_controller

router = APIRouter()


@router.post('/signup', response_model=TokenResponse)
def signup(payload: SignupRequest):
    return signup_controller(payload)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest):
    return login_controller(payload)
