from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from backend.app.database.database import get_db
from backend.app.schemas.user_schema import (
    PredictionRequest, 
    PredictionResponse, 
    PredictionHistoryResponse
)
from backend.app.services.predict_service import PredictService
from backend.app.utils.security import verify_token  # Now returns user_id

router = APIRouter(prefix="/predict", tags=["Predictions"])
predict_service = PredictService()


@router.post("/", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    user_id: int = Depends(verify_token),  # Token from Authorization header
    db: Session = Depends(get_db)
):
    """Classify text and save to history."""
    try:
        result = predict_service.predict_and_save(db, user_id, request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/history", response_model=PredictionHistoryResponse)
def get_prediction_history(
    user_id: int = Depends(verify_token),  # Token from Authorization header
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's prediction history."""
    result = predict_service.get_user_predictions(db, user_id, limit, offset)
    return result


@router.delete("/history/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    user_id: int = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a prediction record."""
    success = predict_service.delete_prediction(db, user_id, prediction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found"
        )
    return {"message": "Prediction deleted successfully"}