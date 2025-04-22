# Face Detection API

A FastAPI-based face detection and analysis service that can be easily integrated into other projects.

## Features

- Face detection in images
- Real-time processing (user uploads, camera input)
- RESTful API endpoints
- CORS support
- Easy integration with other projects
- Hand/finger extraction
- Document upload for KYC
- Selfie upload for face verification

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### As a Package

You can use the face, hand, and document detection functionality in your own Python projects:

```python
from face_detection.core import FaceDetector

# Initialize the detector
detector = FaceDetector()

# Process an image
with open("image.jpg", "rb") as f:
    image_data = f.read()
    result = detector.process_image(image_data)
    print(f"Found {result['faces_detected']} faces")
```

### As an API (Real-Time & Batch Processing)

1. Start the API server:
```bash
python -m face_detection.api
```

2. The API will be available at `http://localhost:8000`

3. API Endpoints:
- `POST /detect-faces`: Upload an image for face detection
- `POST /api/v1/fingerprint/extract-fingers`: Upload a hand image for finger extraction (returns number of fingers, finger crops, and contour image)
- `POST /api/v1/kyc/upload-document`: Upload an ID/passport document for KYC session
- `POST /api/v1/kyc/upload-selfie`: Upload a selfie for face verification
- `GET /test`: Test endpoint that creates and processes a test face pattern
- `GET /`: Root endpoint to check if the API is running

4. Example API usage (face detection and hand/finger extraction):
```python
import requests

# Test endpoint
response = requests.get("http://localhost:8000/test")
print(response.json())

# Detect faces in an image
with open("image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/detect-faces", files=files)
    print(response.json())

# Extract fingers from a hand image
with open("hand.jpg", "rb") as f:
    files = {"image": ("hand.jpg", f, "image/jpeg")}
    response = requests.post("http://localhost:8000/api/v1/fingerprint/extract-fingers", files=files)
    print(response.json())
```

### Batch Processing with Public Datasets

You can benchmark or test the system using public datasets such as [11K Hands](https://sites.google.com/view/11khands/) for hand/finger extraction, [MIDV-500](https://github.com/fal-ko/MIDV-500) for ID documents, or [VGGFace2](https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/) for face verification.

A batch processing script (`batch_finger_extraction.py`) is provided to run extraction over all images in a dataset folder:

```bash
python batch_finger_extraction.py
```

Update the `DATASET_DIR` variable in the script to point to your dataset images.

## API Response Format

The API returns JSON responses with the following structure (example for face detection):

```json
{
    "faces_detected": 1,
    "face_locations": [[x, y, width, height]],
    "processed_image": "base64_encoded_image"
}
```

For hand/finger extraction:
```json
{
    "num_fingers": 5,
    "fingers": ["base64_encoded_finger1", ...],
    "finger_lines": ["base64_encoded_edges1", ...],
    "contour_img": "base64_encoded_hand_contour"
}
```

## Real-Time Processing Note

> This system is designed for real-time, user-driven biometric verification. All processing is performed live on user-uploaded images or camera captures, simulating real-world onboarding scenarios. However, the API and batch scripts can also be used for benchmarking with public datasets.

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest tests/
```

## License

MIT License 