from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core import FaceDetector
import uvicorn
from typing import Dict, Any
import cv2

app = FastAPI(
    title="Face Detection API",
    description="A FastAPI-based face detection and analysis service",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize face detector
face_detector = FaceDetector()

@app.post("/detect-faces")
async def detect_faces(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Detect faces in an uploaded image.
    
    Args:
        file: Image file to process
        
    Returns:
        Dictionary containing detection results
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_data = await file.read()
        result = face_detector.process_image(image_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test() -> Dict[str, Any]:
    """
    Test endpoint that creates and processes a test face pattern.
    
    Returns:
        Dictionary containing test results
    """
    try:
        test_image = face_detector.create_test_face()
        _, buffer = cv2.imencode('.jpg', test_image)
        image_data = buffer.tobytes()
        result = face_detector.process_image(image_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Face Detection API is running"}

if __name__ == "__main__":
    uvicorn.run("face_detection.api:app", host="0.0.0.0", port=8000, reload=True) 