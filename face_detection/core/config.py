from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Face Detection API"
    
    # Face Detection Settings
    FACE_DETECTION_THRESHOLD: float = 0.6
    
    # File Settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png"}
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings() 