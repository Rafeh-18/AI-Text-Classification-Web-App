import os
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Handles model training, validation, and persistence.
    Uses TF-IDF + Logistic Regression for production-ready text classification.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'max_features': 10000,
            'ngram_range': (1, 2),
            'min_df': 5,
            'max_df': 0.8,
            'test_size': 0.2,
            'random_state': 42
        }
        self.pipeline = None
        self.metrics = {}
        
    def load_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load combined dataset from CSV.
        """
        logger.info(f"Loading training data from {data_path}")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Training data not found: {data_path}")
        
        df = pd.read_csv(data_path)
        
        required_cols = ['text', 'combined_label']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Drop any rows with missing text
        df = df.dropna(subset=['text', 'combined_label'])
        df = df[df['text'].str.len() > 0]
        
        X = df['text'].values
        y = df['combined_label'].values
        
        logger.info(f"Loaded {len(X)} samples with {len(np.unique(y))} classes")
        return X, y
    
    def build_pipeline(self) -> Pipeline:
        """
        Construct sklearn pipeline with TF-IDF vectorizer and classifier.
        """
        vectorizer = TfidfVectorizer(
            max_features=self.config['max_features'],
            ngram_range=self.config['ngram_range'],
            min_df=self.config['min_df'],
            max_df=self.config['max_df'],
            sublinear_tf=True,
            strip_accents='unicode',
            stop_words='english'
        )
        
        # Note: multi_class parameter removed (deprecated in sklearn 1.5+)
        classifier = LogisticRegression(
            max_iter=1000,
            solver='lbfgs',
            C=1.0,
            class_weight='balanced',
            random_state=self.config['random_state'],
            n_jobs=-1
        )
        
        pipeline = Pipeline([
            ('tfidf', vectorizer),
            ('classifier', classifier)
        ])
        
        logger.info("Model pipeline constructed successfully")
        return pipeline
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Pipeline:
        """
        Train the model with train/validation split.
        """
        logger.info("Starting model training...")
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=self.config['test_size'],
            random_state=self.config['random_state'],
            stratify=y
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Validation set: {len(X_val)} samples")
        
        self.pipeline = self.build_pipeline()
        self.pipeline.fit(X_train, y_train)
        
        # Evaluate on validation set
        y_pred = self.pipeline.predict(X_val)
        self.metrics = {
            'accuracy': float(accuracy_score(y_val, y_pred)),
            'cross_val_score': float(cross_val_score(
                self.pipeline, X_val, y_val, cv=5, n_jobs=-1
            ).mean()),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'num_classes': len(np.unique(y))
        }
        
        logger.info(f"Validation Accuracy: {self.metrics['accuracy']:.4f}")
        logger.info(f"Cross-Validation Score: {self.metrics['cross_val_score']:.4f}")
        
        return self.pipeline
    
    def save_model(self, model_path: str, label_mapping_path: str = None) -> None:
        """
        Persist trained model and vectorizer to disk.
        """
        if self.pipeline is None:
            raise RuntimeError("No model to save. Train first.")
        
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.pipeline, model_path)
        logger.info(f"Model saved to {model_path}")
        
        if label_mapping_path:
            classifier = self.pipeline.named_steps['classifier']
            label_mapping = {
                str(i): label for i, label in enumerate(classifier.classes_)
            }
            with open(label_mapping_path, 'w') as f:
                json.dump(label_mapping, f, indent=2)
            logger.info(f"Label mapping saved to {label_mapping_path}")
    
    def load_model(self, model_path: str) -> Pipeline:
        """
        Load trained model from disk.
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.pipeline = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")
        return self.pipeline


def train_model(config: Dict[str, Any] = None):
    """
    Main training function.
    """
    trainer = ModelTrainer(config)
    
    # Paths
    data_path = 'backend/app/ml/artifacts/combined_dataset.csv'
    model_path = 'backend/app/ml/models/text_classifier.joblib'
    label_path = 'backend/app/ml/models/label_mapping.json'
    metrics_path = 'backend/app/ml/models/training_metrics.json'
    
    # Load data
    X, y = trainer.load_data(data_path)
    
    # Train model
    trainer.train(X, y)
    
    # Save artifacts
    trainer.save_model(model_path, label_path)
    
    # Save metrics
    with open(metrics_path, 'w') as f:
        json.dump(trainer.metrics, f, indent=2)
    logger.info(f"Training metrics saved to {metrics_path}")
    
    logger.info("Training pipeline complete")
    return trainer, trainer.metrics


if __name__ == '__main__':
    trainer, metrics = train_model()
    print(f"\nTraining Complete!")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Classes: {metrics['num_classes']}")