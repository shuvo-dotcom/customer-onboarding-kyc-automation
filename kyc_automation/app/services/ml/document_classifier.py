import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Any, List
import joblib
import os
from ...core.config import settings

class DocumentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english'
        )
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.classes = [
            'passport',
            'driver_license',
            'national_id',
            'utility_bill',
            'bank_statement',
            'other'
        ]
        self.model_path = 'models/document_classifier.joblib'
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Load existing model or train a new one if not found."""
        if os.path.exists(self.model_path):
            self.vectorizer, self.classifier = joblib.load(self.model_path)
        else:
            # Train with sample data (in production, this would use real training data)
            self._train_with_sample_data()

    def _train_with_sample_data(self):
        """Train the model with sample data."""
        # Sample training data (in production, this would be replaced with real data)
        sample_texts = [
            "PASSPORT REPUBLIC OF INDIA",
            "DRIVER LICENSE STATE OF CALIFORNIA",
            "NATIONAL IDENTITY CARD",
            "ELECTRICITY BILL",
            "BANK STATEMENT",
            "RANDOM DOCUMENT"
        ]
        sample_labels = [0, 1, 2, 3, 4, 5]  # Corresponding to self.classes

        X = self.vectorizer.fit_transform(sample_texts)
        self.classifier.fit(X, sample_labels)
        
        # Save the trained model
        joblib.dump((self.vectorizer, self.classifier), self.model_path)

    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        Classify a document based on its text content.
        
        Args:
            text: The text content of the document
            
        Returns:
            Dictionary containing classification results
        """
        try:
            # Transform the input text
            X = self.vectorizer.transform([text])
            
            # Get prediction probabilities
            probabilities = self.classifier.predict_proba(X)[0]
            
            # Get the predicted class and its probability
            predicted_class_idx = np.argmax(probabilities)
            predicted_class = self.classes[predicted_class_idx]
            confidence = probabilities[predicted_class_idx]
            
            # Get top 3 predictions
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_3_predictions = [
                {
                    'class': self.classes[idx],
                    'confidence': float(probabilities[idx])
                }
                for idx in top_3_indices
            ]
            
            return {
                'predicted_class': predicted_class,
                'confidence': float(confidence),
                'top_predictions': top_3_predictions,
                'needs_review': confidence < settings.DOCUMENT_CLASSIFICATION_THRESHOLD
            }
            
        except Exception as e:
            raise Exception(f"Error classifying document: {str(e)}")

    def update_model(self, new_texts: List[str], new_labels: List[int]):
        """
        Update the model with new training data.
        
        Args:
            new_texts: List of new document texts
            new_labels: List of corresponding labels
        """
        try:
            # Transform new texts
            X = self.vectorizer.transform(new_texts)
            
            # Update the classifier
            self.classifier.fit(X, new_labels)
            
            # Save the updated model
            joblib.dump((self.vectorizer, self.classifier), self.model_path)
            
        except Exception as e:
            raise Exception(f"Error updating model: {str(e)}") 