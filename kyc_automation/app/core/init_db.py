from .database import engine
from ..models.base import Base
from ..models.kyc import Customer, Document, FacialMatch, ComplianceCheck, Notification

def init_db():
    Base.metadata.create_all(bind=engine) 