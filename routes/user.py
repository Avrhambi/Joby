from fastapi import APIRouter, Depends
from controllers.user import get_profile_controller
from utils.security import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_token(token)


@router.get('/user/me')
def get_user_profile(current_user=Depends(get_current_user)):
    return get_profile_controller(current_user)
