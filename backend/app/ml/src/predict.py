import os
import joblib
import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.pipeline import Pipeline
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PredictionService:
    """
    Production prediction service for text classification.
    Singleton pattern ensures model loaded once per process.
    """
    
    _instance = None
    _model = None
    _label_mapping = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self.load_model()
    
    def load_model(self, model_path: str = None, label_path: str = None) -> None:
        """
        Load model and label mapping from disk.
        """
        if model_path is None:
            model_path = 'backend/app/ml/models/text_classifier.joblib'
        if label_path is None:
            label_path = 'backend/app/ml/models/label_mapping.json'
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found. Run training first: {model_path}"
            )
        
        self._model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
        
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                self._label_mapping = json.load(f)
            logger.info(f"Label mapping loaded from {label_path}")
        else:
            classifier = self._model.named_steps['classifier']
            self._label_mapping = {
                str(i): label for i, label in enumerate(classifier.classes_)
            }
    
    def predict(self, text: str) -> Dict[str, Any]:
        """
        Predict class for single text input.
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string")
        
        prediction = self._model.predict([text])[0]
        probabilities = self._model.predict_proba([text])[0]
        classes = self._model.classes_
        
        confidence_scores = {
            str(classes[i]): float(prob) for i, prob in enumerate(probabilities)
        }
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        top_predictions = [
            {'label': str(classes[i]), 'confidence': float(probabilities[i])}
            for i in top_indices
        ]
        
        result = {
            'prediction': prediction,
            'confidence': float(max(probabilities)),
            'top_3': top_predictions,
            'all_scores': confidence_scores,
            'source': self._extract_source(prediction)
        }
        
        logger.debug(f"Prediction: {prediction} (confidence: {result['confidence']:.4f})")
        return result
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Batch prediction for multiple texts.
        """
        if not texts:
            return []
        
        if not all(isinstance(t, str) for t in texts):
            raise ValueError("All inputs must be strings")
        
        predictions = self._model.predict(texts)
        probabilities = self._model.predict_proba(texts)
        classes = self._model.classes_
        
        results = []
        for i, text in enumerate(texts):
            probs = probabilities[i]
            top_indices = np.argsort(probs)[::-1][:3]
            
            results.append({
                'text': text[:100] + '...' if len(text) > 100 else text,
                'prediction': predictions[i],
                'confidence': float(max(probs)),
                'top_3': [
                    {'label': str(classes[j]), 'confidence': float(probs[j])}
                    for j in top_indices
                ],
                'source': self._extract_source(predictions[i])
            })
        
        return results
    
    def _extract_source(self, label: str) -> str:
        """
        Extract dataset source from hierarchical label.
        e.g., 'imdb_positive' -> 'imdb'
        """
        if '_' in str(label):
            return str(label).split('_')[0]
        return 'unknown'
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Return model metadata for monitoring.
        """
        if self._model is None:
            return {'status': 'not_loaded'}
        
        vectorizer = self._model.named_steps['tfidf']
        classifier = self._model.named_steps['classifier']
        
        return {
            'status': 'loaded',
            'num_classes': len(classifier.classes_),
            'vocabulary_size': len(vectorizer.vocabulary_),
            'classes': [str(c) for c in classifier.classes_],
            'label_mapping': self._label_mapping
        }


def get_prediction_service() -> PredictionService:
    """
    Factory function for prediction service.
    """
    return PredictionService()


if __name__ == '__main__':
    service = get_prediction_service()
    
    test_texts = [
        "This movie was absolutely fantastic! Best film I've seen all year.",
        "Terrible product. Waste of money. Would not recommend.",
        "The discussion about quantum physics was fascinating.",
        "I love this restaurant. Great food and service."
    ]
    
    print("Testing prediction service...")
    print("=" * 60)
    
    for text in test_texts:
        result = service.predict(text)
        print(f"\nText: {text[:60]}...")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Source: {result['source']}")
        print(f"Top 3:")
        for pred in result['top_3']:
            print(f"  - {pred['label']}: {pred['confidence']:.4f}")
    
    print("\n" + "=" * 60)
    print("Model Info:")
    info = service.get_model_info()
    print(f"Status: {info['status']}")
    print(f"Classes: {info['num_classes']}")
    print(f"Vocabulary: {info['vocabulary_size']}")