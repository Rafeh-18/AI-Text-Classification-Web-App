from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user_model import User
from backend.app.schemas.user_schema import UserCreate, UserLogin
from backend.app.utils.security import create_access_token
from typing import Optional


class AuthService:

    @staticmethod
    def register(db: Session, user_data: UserCreate) -> User:
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValueError("Email already registered")

        if db.query(User).filter(User.username == user_data.username).first():
            raise ValueError("Username already taken")

        user = User(email=user_data.email, username=user_data.username)
        user.set_password(user_data.password)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Registration failed")

    @staticmethod
    def login(db: Session, credentials: UserLogin) -> dict:
        user = db.query(User).filter(User.email == credentials.email).first()

        if not user or not user.verify_password(credentials.password):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is deactivated")

        # Fixed: sub must be a string — integer sub causes JWT encode/decode
        # failures with some versions of python-jose
        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()