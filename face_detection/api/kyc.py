import tempfile
import os
import requests
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
from PIL import Image
from dotenv import load_dotenv

router = APIRouter()

# Load Face++ credentials from .env
load_dotenv()
FACEPP_API_KEY = os.getenv("FACEPP_API_KEY")
FACEPP_API_SECRET = os.getenv("FACEPP_API_SECRET")
FACEPP_DETECT_URL = "https://api-us.faceplusplus.com/facepp/v3/detect"
FACEPP_COMPARE_URL = "https://api-us.faceplusplus.com/facepp/v3/compare"

if not FACEPP_API_KEY or not FACEPP_API_SECRET:
    raise RuntimeError("Face++ API credentials not set in environment variables!")

# In-memory store for KYC sessions (for demo)
kyc_sessions = {}

@router.post("/kyc/upload-document")
async def upload_document(document: UploadFile = File(...)) -> Dict:
    """
    Upload a document image (ID/passport), extract face using Face++ and store face_token.
    """
    if not document.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        content = await document.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Send to Face++ for face detection (use more accurate model and return more debug info)
    with open(temp_file_path, 'rb') as img_file:
        resp = requests.post(
            FACEPP_DETECT_URL,
            data={
                'api_key': FACEPP_API_KEY,
                'api_secret': FACEPP_API_SECRET,
                'return_landmark': 1,
                'return_attributes': 'none',
                'model': 'detection_02',
            },
            files={'image_file': img_file}
        )
    os.unlink(temp_file_path)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Face++ error: {resp.text}")
    data = resp.json()
    faces = data.get('faces', [])
    if not faces:
        raise HTTPException(status_code=400, detail="No face found in document")
    face_token = faces[0]['face_token']

    # Store session
    session_id = face_token
    kyc_sessions[session_id] = {
        "document_face_token": face_token,
        "document_detect_response": data,  # Store full detect response for debugging
    }

    return {
        "session_id": session_id,
        "face_found": True,
        "detect_debug": data  # Return full Face++ detect response for debugging
    }

@router.post("/kyc/upload-selfie")
async def upload_selfie(session_id: str, selfie: UploadFile = File(...)) -> Dict:
    """
    Upload a live selfie and verify against document face using Face++.
    """
    if session_id not in kyc_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    if not selfie.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        content = await selfie.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Detect face in selfie to get face_token (use more accurate model)
    with open(temp_file_path, 'rb') as img_file:
        resp = requests.post(
            FACEPP_DETECT_URL,
            data={
                'api_key': FACEPP_API_KEY,
                'api_secret': FACEPP_API_SECRET,
                'return_landmark': 1,
                'return_attributes': 'none',
                'model': 'detection_02',
            },
            files={'image_file': img_file}
        )
    os.unlink(temp_file_path)
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Face++ error: {resp.text}")
    data = resp.json()
    faces = data.get('faces', [])
    if not faces:
        raise HTTPException(status_code=400, detail="No face found in selfie")
    selfie_face_token = faces[0]['face_token']

    # Compare document and selfie face_token
    resp = requests.post(
        FACEPP_COMPARE_URL,
        data={
            'api_key': FACEPP_API_KEY,
            'api_secret': FACEPP_API_SECRET,
            'face_token1': kyc_sessions[session_id]["document_face_token"],
            'face_token2': selfie_face_token
        }
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Face++ compare error: {resp.text}")
    result = resp.json()
    confidence = result.get('confidence', 0)
    # Always use 80 as the match threshold, regardless of Face++ thresholds
    threshold = 80
    verified = confidence >= threshold

    # Store selfie result
    kyc_sessions[session_id]["selfie_face_token"] = selfie_face_token
    kyc_sessions[session_id]["verified"] = verified
    kyc_sessions[session_id]["confidence"] = confidence
    kyc_sessions[session_id]["threshold"] = threshold
    kyc_sessions[session_id]["compare_debug"] = result  # Store full compare response for debugging

    return {
        "verified": bool(verified),
        "confidence": confidence,
        "threshold": threshold,
        "compare_debug": result  # Return full compare response for debugging
    }

@router.get("/kyc/session/{session_id}")
def get_session(session_id: str):
    if session_id not in kyc_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return kyc_sessions[session_id]
