from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.database.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)  # Fixed: was Integer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    predictions = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        # Fixed: was hashlib.sha256 — unsafe, no salt
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        # Fixed: was sha256 comparison
        return pwd_context.verify(password, self.hashed_password)


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_text = Column(Text, nullable=False)
    prediction = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    top_predictions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="predictions")