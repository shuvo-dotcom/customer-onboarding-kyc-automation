from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "KYC Automation Agent"
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/kyc_db")
    
    # Compliance API Settings
    COMPLYADVANTAGE_API_KEY: Optional[str] = os.getenv("COMPLYADVANTAGE_API_KEY")
    COMPLYADVANTAGE_API_URL: str = os.getenv("COMPLYADVANTAGE_API_URL", "https://api.complyadvantage.com")
    
    # Notification Settings
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    
    # Facial Recognition Settings
    FACIAL_MATCH_THRESHOLD: float = float(os.getenv("FACIAL_MATCH_THRESHOLD", "0.9"))
    
    # Document Classification Settings
    DOCUMENT_CLASSIFICATION_THRESHOLD: float = float(os.getenv("DOCUMENT_CLASSIFICATION_THRESHOLD", "0.85"))
    
    # OCR Settings
    USE_AWS_TEXTRACT: bool = os.getenv("USE_AWS_TEXTRACT", "true").lower() == "true"
    
    class Config:
        case_sensitive = True

settings = Settings() 