from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database.database import get_db
from backend.app.schemas.user_schema import UserCreate, UserLogin, UserResponse, Token
from backend.app.services.auth_service import AuthService
from backend.app.utils.security import verify_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_ UserCreate, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    try:
        result = AuthService.login(db, credentials)
        return {"access_token": result["access_token"], "token_type": result["token_type"]}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_current_user(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user