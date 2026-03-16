from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.schemas.user_schema import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.auth_service import AuthService
from backend.app.utils.security import verify_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    try:
        user = AuthService.register(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get access token.
    """
    try:
        result = AuthService.login(db, credentials)
        return {
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user.
    """
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user