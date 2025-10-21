from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class TokenResponse(BaseModel):
    token: str
    user: UserResponse
