from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserBasic"


class RefreshRequest(BaseModel):
    refresh_token: str


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class UserBasic(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_email_verified: bool

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
