from deepface import DeepFace
import cv2
import numpy as np
from typing import Dict, Any, Tuple
from ...core.config import settings

class FaceMatcher:
    def __init__(self):
        self.model_name = "VGG-Face"
        self.detector_backend = "opencv"
        self.distance_metric = "cosine"

    def extract_face(self, image_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Extract face from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple containing face image and face detection results
        """
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("Could not read image file")

            # Detect face
            face_objs = DeepFace.extract_faces(
                img_path=image_path,
                target_size=(224, 224),
                detector_backend=self.detector_backend
            )
            
            if not face_objs:
                raise Exception("No face detected in image")
            
            # Get the first detected face
            face_obj = face_objs[0]
            face_img = face_obj['face']
            face_region = face_obj['facial_area']
            
            return face_img, face_region
            
        except Exception as e:
            raise Exception(f"Error extracting face: {str(e)}")

    def compare_faces(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """
        Compare two faces and calculate similarity score.
        
        Args:
            img1_path: Path to the first image
            img2_path: Path to the second image
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            # Extract faces
            face1_img, face1_region = self.extract_face(img1_path)
            face2_img, face2_region = self.extract_face(img2_path)
            
            # Compare faces
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                distance_metric=self.distance_metric
            )
            
            # Calculate similarity score (convert distance to similarity)
            distance = result['distance']
            similarity = 1 - distance
            
            return {
                'similarity_score': float(similarity),
                'verified': similarity >= settings.FACIAL_MATCH_THRESHOLD,
                'face1_region': face1_region,
                'face2_region': face2_region,
                'model': self.model_name,
                'threshold': settings.FACIAL_MATCH_THRESHOLD
            }
            
        except Exception as e:
            raise Exception(f"Error comparing faces: {str(e)}")

    def analyze_face(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze facial attributes.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing facial analysis results
        """
        try:
            # Analyze face
            demography = DeepFace.analyze(
                img_path=image_path,
                detector_backend=self.detector_backend
            )
            
            return {
                'age': demography['age'],
                'gender': demography['gender'],
                'race': demography['race'],
                'emotion': demography['emotion'],
                'face_region': demography['region']
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing face: {str(e)}")

    def detect_spoofing(self, image_path: str) -> Dict[str, Any]:
        """
        Detect potential spoofing attempts.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing spoofing detection results
        """
        try:
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("Could not read image file")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate image quality metrics
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Basic spoofing detection rules
            is_spoofed = (
                blur_score < 100 or  # Too blurry
                brightness < 50 or    # Too dark
                brightness > 200 or   # Too bright
                contrast < 20         # Too low contrast
            )
            
            return {
                'is_spoofed': bool(is_spoofed),
                'blur_score': float(blur_score),
                'brightness': float(brightness),
                'contrast': float(contrast),
                'confidence': 1.0 if is_spoofed else 0.0
            }
            
        except Exception as e:
            raise Exception(f"Error detecting spoofing: {str(e)}") 