from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import face_recognition
import tempfile
import os
from typing import Dict
from ..core.config import settings
from .kyc import router as kyc_router
from .fingerprint import router as fingerprint_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

def validate_image_file(file: UploadFile) -> None:
    """Validate the uploaded image file"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    extension = file.filename.split('.')[-1].lower()
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension not allowed. Allowed extensions: {settings.ALLOWED_EXTENSIONS}"
        )

@app.post(f"{settings.API_V1_STR}/detect-face")
async def detect_face(image: UploadFile = File(...)) -> Dict:
    """
    Detect faces in the uploaded image
    """
    try:
        validate_image_file(image)
        
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            content = await image.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Load the image
        image = face_recognition.load_image_file(temp_file_path)
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(image)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if not face_locations:
            return {
                "status": "success",
                "face_detected": False,
                "message": "No face detected in the image"
            }
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        return {
            "status": "success",
            "face_detected": True,
            "face_count": len(face_locations),
            "face_locations": face_locations,
            "face_encodings": [encoding.tolist() for encoding in face_encodings]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/verify-faces")
async def verify_faces(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...)
) -> Dict:
    """
    Verify if the faces in two images match
    """
    try:
        validate_image_file(image1)
        validate_image_file(image2)
        
        # Save both uploaded files temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file1:
            content1 = await image1.read()
            temp_file1.write(content1)
            temp_file1_path = temp_file1.name

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file2:
            content2 = await image2.read()
            temp_file2.write(content2)
            temp_file2_path = temp_file2.name

        # Load the images
        image1 = face_recognition.load_image_file(temp_file1_path)
        image2 = face_recognition.load_image_file(temp_file2_path)
        
        # Get face encodings
        face_encodings1 = face_recognition.face_encodings(image1)
        face_encodings2 = face_recognition.face_encodings(image2)
        
        # Clean up temporary files
        os.unlink(temp_file1_path)
        os.unlink(temp_file2_path)
        
        if not face_encodings1 or not face_encodings2:
            raise HTTPException(
                status_code=400,
                detail="Could not find faces in one or both images"
            )
        
        # Compare faces
        results = face_recognition.compare_faces(
            [face_encodings1[0]],  # Compare first face from first image
            face_encodings2[0]     # with first face from second image
        )
        
        # Calculate face distance
        face_distance = face_recognition.face_distance(
            [face_encodings1[0]],
            face_encodings2[0]
        )[0]
        
        return {
            "status": "success",
            "verified": results[0],
            "distance": float(face_distance),
            "threshold": 0.6  # Standard threshold for face recognition
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(kyc_router, prefix="/api/v1")
app.include_router(fingerprint_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Face Detection API is running"} 