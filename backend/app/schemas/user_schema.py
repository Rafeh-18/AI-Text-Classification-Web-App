from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Prediction Schemas
class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=10000)


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    top_3: List[Dict[str, Any]]
    source: str
    saved: bool = True


class PredictionHistoryItem(BaseModel):
    id: int
    input_text: str
    prediction: str
    confidence: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    total: int
    predictions: List[PredictionHistoryItem]