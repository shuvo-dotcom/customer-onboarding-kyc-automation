from sqlalchemy import Column, String, JSON, Boolean, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"
    
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected, needs_review
    
    # Relationships
    documents = relationship("Document", back_populates="customer")
    facial_matches = relationship("FacialMatch", back_populates="customer")
    compliance_checks = relationship("ComplianceCheck", back_populates="customer")

class Document(BaseModel):
    __tablename__ = "documents"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    document_type = Column(String, nullable=False)  # passport, driver_license, utility_bill, etc.
    document_number = Column(String)
    file_path = Column(String, nullable=False)
    extracted_data = Column(JSON)
    classification_score = Column(Float)
    status = Column(String, default="pending")  # pending, verified, rejected
    
    # Relationships
    customer = relationship("Customer", back_populates="documents")

class FacialMatch(BaseModel):
    __tablename__ = "facial_matches"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    selfie_path = Column(String, nullable=False)
    id_document_path = Column(String, nullable=False)
    similarity_score = Column(Float)
    status = Column(String, default="pending")  # pending, matched, not_matched
    
    # Relationships
    customer = relationship("Customer", back_populates="facial_matches")

class ComplianceCheck(BaseModel):
    __tablename__ = "compliance_checks"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    check_type = Column(String, nullable=False)  # sanctions, pep, adverse_media
    result = Column(JSON)
    status = Column(String, default="pending")  # pending, clear, flagged
    
    # Relationships
    customer = relationship("Customer", back_populates="compliance_checks")

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    customer_id = Column(Integer, ForeignKey("customers.id"))
    notification_type = Column(String, nullable=False)  # email, sms
    content = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed
    delivery_status = Column(JSON) 