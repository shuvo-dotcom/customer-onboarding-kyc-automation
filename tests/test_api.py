import pytest
import requests
import os
from pathlib import Path

API_URL = "http://localhost:8000/api/v1"
TEST_IMAGES_DIR = Path(__file__).parent.parent / "test_images"

@pytest.fixture
def test_images():
    """Ensure test images directory exists"""
    os.makedirs(TEST_IMAGES_DIR, exist_ok=True)
    return TEST_IMAGES_DIR

def test_detect_face_success(test_images):
    """Test successful face detection"""
    image_path = test_images / "face.jpg"
    if not image_path.exists():
        pytest.skip("Test image not found")
    
    with open(image_path, "rb") as f:
        files = {"image": ("face.jpg", f, "image/jpeg")}
        response = requests.post(f"{API_URL}/detect-face", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["face_detected"] is True
    assert "analysis" in data

def test_detect_face_no_face(test_images):
    """Test face detection with no face in image"""
    image_path = test_images / "no_face.jpg"
    if not image_path.exists():
        pytest.skip("Test image not found")
    
    with open(image_path, "rb") as f:
        files = {"image": ("no_face.jpg", f, "image/jpeg")}
        response = requests.post(f"{API_URL}/detect-face", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["face_detected"] is False
    assert "message" in data

def test_verify_faces_success(test_images):
    """Test successful face verification"""
    image1_path = test_images / "face1.jpg"
    image2_path = test_images / "face2.jpg"
    if not (image1_path.exists() and image2_path.exists()):
        pytest.skip("Test images not found")
    
    with open(image1_path, "rb") as f1, open(image2_path, "rb") as f2:
        files = {
            "image1": ("face1.jpg", f1, "image/jpeg"),
            "image2": ("face2.jpg", f2, "image/jpeg")
        }
        response = requests.post(f"{API_URL}/verify-faces", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "verified" in data
    assert "distance" in data
    assert "threshold" in data

def test_verify_faces_invalid_image():
    """Test face verification with invalid image"""
    files = {
        "image1": ("invalid.txt", b"not an image", "text/plain"),
        "image2": ("invalid.txt", b"not an image", "text/plain")
    }
    response = requests.post(f"{API_URL}/verify-faces", files=files)
    
    assert response.status_code == 400
    assert "File must be an image" in response.text

def test_api_root():
    """Test API root endpoint"""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Face Detection API is running" 