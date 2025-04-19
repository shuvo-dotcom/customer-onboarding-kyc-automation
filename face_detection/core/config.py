from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Face Detection API"
    
    # Face Detection Settings
    FACE_DETECTION_MODEL: str = "VGG-Face"
    FACE_DETECTION_BACKEND: str = "opencv"
    FACE_DETECTION_METRIC: str = "cosine"
    
    # Analysis Settings
    FACE_ANALYSIS_ACTIONS: list = ["age", "gender", "emotion"]
    
    # File Settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}
    
    class Config:
        case_sensitive = True

settings = Settings() 