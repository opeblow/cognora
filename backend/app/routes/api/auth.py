from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import (
    SignUpRequest, LoginRequest, TokenResponse, ForgotPasswordRequest,
    ResetPasswordRequest, VerifyEmailRequest, UserResponse,
    RefreshTokenRequest, ChangePasswordRequest,
)
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        result = service.signup(request.email, request.password, request.full_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        result = service.login(request.email, request.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/verify-email", response_model=dict)
def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        service.verify_email(request.token)
        return {"message": "Email verified successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/forgot-password", response_model=dict)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.forgot_password(request.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", response_model=dict)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        service.reset_password(request.token, request.password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh", response_model=dict)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        result = service.refresh_token(request.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/change-password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    try:
        service.change_password(str(current_user.id), request.current_password, request.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "is_verified": current_user.is_verified,
        "credits": current_user.credits,
        "learning_streak": current_user.learning_streak,
    }


@router.get("/google/login")
def google_login():
    auth_url = AuthService.get_google_auth_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
def google_callback(code: str, error: str = None, db: Session = Depends(get_db)):
    service = AuthService(db)
    if error:
        raise HTTPException(status_code=400, detail="Google OAuth failed")
    try:
        result = service.google_auth(code)
        params = urlencode({
            "token": result["access_token"],
            "refresh_token": result["refresh_token"],
        })
        frontend_url = settings.APP_URL or "http://localhost:3000"
        return RedirectResponse(url=f"{frontend_url}/auth/callback?{params}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
