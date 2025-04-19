from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Document(BaseModel):
    id: int
    customer_id: int
    document_type: str
    document_number: Optional[str] = None
    file_path: str
    extracted_data: Optional[Dict[str, Any]] = None
    classification_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FacialMatch(BaseModel):
    id: int
    customer_id: int
    selfie_path: str
    id_document_path: str
    similarity_score: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplianceCheck(BaseModel):
    id: int
    customer_id: int
    check_type: str
    result: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Notification(BaseModel):
    id: int
    customer_id: int
    notification_type: str
    content: str
    status: str
    delivery_status: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class KYCResponse(BaseModel):
    customer: Customer
    documents: List[Document]
    facial_match: Optional[FacialMatch] = None
    compliance_checks: List[ComplianceCheck]
    notifications: List[Notification]

    class Config:
        from_attributes = True 