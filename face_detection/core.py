import cv2
import numpy as np
from typing import List, Tuple, Dict, Any
import base64
from io import BytesIO
from PIL import Image

class FaceDetector:
    """Core face detection and analysis functionality."""
    
    def __init__(self):
        """Initialize the face detector with required models."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of face coordinates (x, y, width, height)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces.tolist() if len(faces) > 0 else []
    
    def draw_faces(self, image: np.ndarray, faces: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Draw rectangles around detected faces.
        
        Args:
            image: Input image as numpy array
            faces: List of face coordinates
            
        Returns:
            Image with face rectangles drawn
        """
        result = image.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(result, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return result
    
    def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Process an image and detect faces.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Dictionary containing detection results
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Detect faces
        faces = self.detect_faces(img)
        
        # Draw faces on image
        result_img = self.draw_faces(img, faces)
        
        # Convert result image to base64
        _, buffer = cv2.imencode('.jpg', result_img)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "faces_detected": len(faces),
            "face_locations": faces,
            "processed_image": result_base64
        }
    
    @staticmethod
    def create_test_face() -> np.ndarray:
        """
        Create a test face pattern for testing.
        
        Returns:
            Test image as numpy array
        """
        img = np.zeros((200, 200, 3), dtype=np.uint8)
        img[:] = (255, 255, 255)  # White background
        
        # Draw a circle for the face
        cv2.circle(img, (100, 100), 60, (200, 200, 200), -1)
        
        # Draw eyes
        cv2.circle(img, (70, 80), 10, (0, 0, 0), -1)  # Left eye
        cv2.circle(img, (130, 80), 10, (0, 0, 0), -1)  # Right eye
        
        # Draw mouth
        cv2.ellipse(img, (100, 130), (30, 20), 0, 0, 180, (0, 0, 0), 2)
        
        return img 