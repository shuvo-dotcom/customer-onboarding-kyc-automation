# Face Detection API

A FastAPI-based face detection and verification system that provides endpoints for:
- Face detection with analysis (age, gender, emotion)
- Face verification between two images

## Features

- Face detection and analysis
- Face verification
- Real-time processing
- RESTful API endpoints
- CORS support
- Comprehensive test suite
- Configurable settings

## Project Structure

```
face_detection/
├── api/           # API endpoints
├── core/          # Core configuration
├── models/        # Data models
└── utils/         # Utility functions
tests/             # Test suite
test_images/       # Test images
```

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

## Running the API Locally

Start the FastAPI server:
```bash
uvicorn face_detection.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- Main endpoint: http://localhost:8000
- API documentation: http://localhost:8000/docs
- API v1 documentation: http://localhost:8000/api/v1/docs

## Deployment to Render

1. Create a Render account at https://render.com

2. Create a new Web Service:
   - Connect your GitHub repository
   - Select the branch to deploy
   - The configuration will be automatically picked up from your `render.yaml` file

3. Environment Variables (already configured in render.yaml):
   - `PYTHON_VERSION`: 3.11.0
   - `FACE_DETECTION_MODEL`: VGG-Face
   - `FACE_DETECTION_BACKEND`: opencv
   - `FACE_DETECTION_METRIC`: cosine
   - `FACE_ANALYSIS_ACTIONS`: ["age", "gender", "emotion"]
   - `TF_CPP_MIN_LOG_LEVEL`: 2
   - `TF_ENABLE_ONEDNN_OPTS`: 1
   - `TF_XLA_FLAGS`: --tf_xla_enable_xla_devices

4. Click "Create Web Service"

The API will be automatically deployed and available at your Render URL.

## API Endpoints

### 1. Detect Face
- **Endpoint**: `/api/v1/detect-face`
- **Method**: POST
- **Input**: Image file
- **Output**: Face analysis (age, gender, emotion)

### 2. Verify Faces
- **Endpoint**: `/api/v1/verify-faces`
- **Method**: POST
- **Input**: Two image files
- **Output**: Verification result with confidence score

## Testing

Run the test suite:
```bash
pytest tests/
```

Make sure to place test images in the `test_images` directory:
- `face.jpg` for face detection
- `no_face.jpg` for testing no face detection
- `face1.jpg` and `face2.jpg` for face verification

## Configuration

The API can be configured through environment variables or by modifying `face_detection/core/config.py`:

- `FACE_DETECTION_MODEL`: Model used for face detection (default: "VGG-Face")
- `FACE_DETECTION_BACKEND`: Backend used for face detection (default: "opencv")
- `FACE_DETECTION_METRIC`: Distance metric for face verification (default: "cosine")
- `FACE_ANALYSIS_ACTIONS`: List of analysis actions (default: ["age", "gender", "emotion"])

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 