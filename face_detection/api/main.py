from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
from deepface import DeepFace
import tempfile
import os
from typing import Dict
from ..core.config import settings

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
async def detect_face(
    image: UploadFile = File(...),
    validate: bool = Depends(validate_image_file)
) -> Dict:
    """
    Detect faces in the uploaded image and provide analysis
    """
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
            content = await image.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Read the image
        img = cv2.imread(temp_file_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        # Detect faces using DeepFace
        try:
            face_analysis = DeepFace.analyze(
                img_path=temp_file_path,
                actions=settings.FACE_ANALYSIS_ACTIONS,
                detector_backend=settings.FACE_DETECTION_BACKEND
            )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return {
                "status": "success",
                "face_detected": True,
                "analysis": face_analysis[0] if isinstance(face_analysis, list) else face_analysis
            }
            
        except Exception as e:
            # Clean up temporary file
            os.unlink(temp_file_path)
            return {
                "status": "success",
                "face_detected": False,
                "message": "No face detected in the image"
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/verify-faces")
async def verify_faces(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    validate1: bool = Depends(validate_image_file),
    validate2: bool = Depends(validate_image_file)
) -> Dict:
    """
    Verify if the faces in two images match
    """
    try:
        # Save both uploaded files temporarily
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file1:
            content1 = await image1.read()
            temp_file1.write(content1)
            temp_file1_path = temp_file1.name

        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file2:
            content2 = await image2.read()
            temp_file2.write(content2)
            temp_file2_path = temp_file2.name

        # Verify faces using DeepFace
        try:
            result = DeepFace.verify(
                img1_path=temp_file1_path,
                img2_path=temp_file2_path,
                model_name=settings.FACE_DETECTION_MODEL,
                detector_backend=settings.FACE_DETECTION_BACKEND,
                distance_metric=settings.FACE_DETECTION_METRIC
            )

            # Clean up temporary files
            os.unlink(temp_file1_path)
            os.unlink(temp_file2_path)

            return {
                "status": "success",
                "verified": result["verified"],
                "distance": float(result["distance"]),
                "threshold": float(result["threshold"]),
                "model": result["model"],
                "detector_backend": result["detector_backend"]
            }

        except Exception as e:
            # Clean up temporary files
            os.unlink(temp_file1_path)
            os.unlink(temp_file2_path)
            raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Face Detection API is running"} 