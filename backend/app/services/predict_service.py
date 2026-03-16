from sqlalchemy.orm import Session
from backend.app.models.user_model import PredictionHistory
from backend.app.ml.src.predict import get_prediction_service
from typing import List, Dict, Any
import json


class PredictService:
    
    def __init__(self):
        self.ml_service = get_prediction_service()
    
    def predict_and_save(self, db: Session, user_id: int, text: str) -> Dict[str, Any]:
        """
        Make prediction and save to history.
        """
        # Get prediction from ML model
        result = self.ml_service.predict(text)
        
        # Save to history
        prediction_record = PredictionHistory(
            user_id=user_id,
            input_text=text,
            prediction=result['prediction'],
            confidence=result['confidence'],
            top_predictions=json.dumps(result['top_3'])
        )
        
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)
        
        return {
            **result,
            'saved': True
        }
    
    def get_user_predictions(self, db: Session, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get user's prediction history.
        """
        query = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).order_by(PredictionHistory.created_at.desc())
        
        total = query.count()
        predictions = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "predictions": predictions
        }
    
    def delete_prediction(self, db: Session, user_id: int, prediction_id: int) -> bool:
        """
        Delete a prediction record.
        """
        record = db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == user_id
        ).first()
        
        if not record:
            return False
        
        db.delete(record)
        db.commit()
        return True