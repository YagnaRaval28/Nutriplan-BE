from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, AuthToken
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshRequest,
    VerifyEmailRequest, ForgotPasswordRequest, ResetPasswordRequest, UserBasic,
)
from app.utils.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, generate_secure_token, hash_token,
)
from app.config import settings
from app.services.email_service import send_verification_email, send_password_reset_email

router = APIRouter()


@router.post("/register", status_code=201)
def register(body: RegisterRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if body.role not in ("user", "dietician", "doctor"):
        raise HTTPException(status_code=400, detail="Invalid role")

    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.flush()

    token_raw = generate_secure_token()
    auth_token = AuthToken(
        user_id=user.id,
        token_hash=hash_token(token_raw),
        token_type="email_verify",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(auth_token)
    db.commit()
    db.refresh(user)

    background_tasks.add_task(send_verification_email, user.email, user.name, token_raw)
    return {"message": "Registration successful. Please verify your email.", "user_id": str(user.id)}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.is_active == True).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token_raw = generate_secure_token()

    db.query(AuthToken).filter(
        AuthToken.user_id == user.id, AuthToken.token_type == "refresh"
    ).delete()

    db.add(AuthToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token_raw),
        token_type="refresh",
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_raw,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserBasic.model_validate(user),
    )


@router.post("/refresh-token")
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    token_record = db.query(AuthToken).filter(
        AuthToken.token_hash == hash_token(body.refresh_token),
        AuthToken.token_type == "refresh",
        AuthToken.used_at == None,
    ).first()
    if not token_record or token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    access_token = create_access_token({"sub": str(user.id), "role": user.role})

    # Rotate refresh token: mark old one used, issue a new one
    token_record.used_at = datetime.now(timezone.utc)
    new_refresh_raw = generate_secure_token()
    db.add(AuthToken(
        user_id=user.id,
        token_hash=hash_token(new_refresh_raw),
        token_type="refresh",
        expires_at=token_record.expires_at,  # keep same expiry window
    ))
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_raw,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/verify-email")
def verify_email(body: VerifyEmailRequest, db: Session = Depends(get_db)):
    token_record = db.query(AuthToken).filter(
        AuthToken.token_hash == hash_token(body.token),
        AuthToken.token_type == "email_verify",
        AuthToken.used_at == None,
    ).first()
    if not token_record or token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.is_email_verified = True
    token_record.used_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        token_raw = generate_secure_token()
        db.add(AuthToken(
            user_id=user.id,
            token_hash=hash_token(token_raw),
            token_type="password_reset",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        ))
        db.commit()
        background_tasks.add_task(send_password_reset_email, user.email, user.name, token_raw)
    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_record = db.query(AuthToken).filter(
        AuthToken.token_hash == hash_token(body.token),
        AuthToken.token_type == "password_reset",
        AuthToken.used_at == None,
    ).first()
    if not token_record or token_record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    user.password_hash = hash_password(body.new_password)
    token_record.used_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Password reset successfully"}


@router.post("/logout")
def logout(db: Session = Depends(get_db), current_user=Depends(__import__("app.utils.security", fromlist=["get_current_user"]).get_current_user)):
    db.query(AuthToken).filter(
        AuthToken.user_id == current_user.id,
        AuthToken.token_type == "refresh",
    ).delete()
    db.commit()
    return {"message": "Logged out successfully"}
