from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime

from .core.config import settings
from .models.kyc import Customer, Document, FacialMatch, ComplianceCheck, Notification
from .schemas.kyc import (
    CustomerCreate,
    Customer as CustomerSchema,
    Document as DocumentSchema,
    FacialMatch as FacialMatchSchema,
    ComplianceCheck as ComplianceCheckSchema,
    Notification as NotificationSchema,
    KYCResponse
)
from .services.ocr.text_extractor import TextExtractor
from .services.ml.document_classifier import DocumentClassifier
from .services.facial.face_matcher import FaceMatcher
from .services.compliance.checker import ComplianceChecker
from .services.notification.notifier import Notifier

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
text_extractor = TextExtractor()
document_classifier = DocumentClassifier()
face_matcher = FaceMatcher()
compliance_checker = ComplianceChecker()
notifier = Notifier()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post(f"{settings.API_V1_STR}/kyc/start", response_model=KYCResponse)
async def start_kyc_process(
    customer_data: CustomerCreate,
    id_document: UploadFile = File(...),
    selfie: UploadFile = File(...),
    address_document: UploadFile = File(...)
):
    """
    Start the KYC verification process.
    """
    try:
        # Save uploaded files
        id_document_path = os.path.join(UPLOAD_DIR, f"id_{datetime.now().timestamp()}_{id_document.filename}")
        selfie_path = os.path.join(UPLOAD_DIR, f"selfie_{datetime.now().timestamp()}_{selfie.filename}")
        address_document_path = os.path.join(UPLOAD_DIR, f"address_{datetime.now().timestamp()}_{address_document.filename}")
        
        with open(id_document_path, "wb") as buffer:
            shutil.copyfileobj(id_document.file, buffer)
        
        with open(selfie_path, "wb") as buffer:
            shutil.copyfileobj(selfie.file, buffer)
        
        with open(address_document_path, "wb") as buffer:
            shutil.copyfileobj(address_document.file, buffer)
        
        # Create customer record
        customer = Customer(
            first_name=customer_data.first_name,
            last_name=customer_data.last_name,
            email=customer_data.email,
            phone=customer_data.phone,
            status="pending"
        )
        
        # Process ID document
        id_document_text = text_extractor.extract_text(id_document_path)
        id_document_class = document_classifier.classify_document(id_document_text['text'])
        
        id_document_record = Document(
            customer=customer,
            document_type=id_document_class['predicted_class'],
            document_number=id_document_text.get('key_value_pairs', {}).get('Document Number'),
            file_path=id_document_path,
            extracted_data=id_document_text,
            classification_score=id_document_class['confidence'],
            status="pending"
        )
        
        # Process address document
        address_document_text = text_extractor.extract_text(address_document_path)
        address_document_class = document_classifier.classify_document(address_document_text['text'])
        
        address_document_record = Document(
            customer=customer,
            document_type=address_document_class['predicted_class'],
            file_path=address_document_path,
            extracted_data=address_document_text,
            classification_score=address_document_class['confidence'],
            status="pending"
        )
        
        # Perform facial matching
        facial_match_result = face_matcher.compare_faces(selfie_path, id_document_path)
        
        facial_match_record = FacialMatch(
            customer=customer,
            selfie_path=selfie_path,
            id_document_path=id_document_path,
            similarity_score=facial_match_result['similarity_score'],
            status="matched" if facial_match_result['verified'] else "not_matched"
        )
        
        # Perform compliance checks
        compliance_result = compliance_checker.perform_all_checks({
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email
        })
        
        compliance_checks = []
        for check_type, result in compliance_result.items():
            if check_type != 'status' and check_type != 'risk_level':
                compliance_check = ComplianceCheck(
                    customer=customer,
                    check_type=check_type,
                    result=result,
                    status=result.get('status', 'pending')
                )
                compliance_checks.append(compliance_check)
        
        # Determine overall KYC status
        if (
            id_document_class['needs_review'] or
            address_document_class['needs_review'] or
            not facial_match_result['verified'] or
            compliance_result['risk_level'] == 'high'
        ):
            customer.status = "needs_review"
            required_actions = []
            
            if id_document_class['needs_review']:
                required_actions.append("ID document verification needs review")
            if address_document_class['needs_review']:
                required_actions.append("Address document verification needs review")
            if not facial_match_result['verified']:
                required_actions.append("Facial verification failed")
            if compliance_result['risk_level'] == 'high':
                required_actions.append("Compliance check requires review")
            
            # Send review notification
            notification_result = notifier.send_kyc_review_notification({
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone
            }, required_actions)
            
            notification = Notification(
                customer=customer,
                notification_type="review",
                content=str(required_actions),
                status=notification_result['email']['status'],
                delivery_status=notification_result
            )
        else:
            customer.status = "approved"
            # Send approval notification
            notification_result = notifier.send_kyc_approval_notification({
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'phone': customer.phone
            })
            
            notification = Notification(
                customer=customer,
                notification_type="approval",
                content="KYC verification approved",
                status=notification_result['email']['status'],
                delivery_status=notification_result
            )
        
        # Save all records to database
        # Note: In a real application, you would use a database session here
        # For this example, we'll just return the response
        
        return KYCResponse(
            customer=CustomerSchema.from_orm(customer),
            documents=[
                DocumentSchema.from_orm(id_document_record),
                DocumentSchema.from_orm(address_document_record)
            ],
            facial_match=FacialMatchSchema.from_orm(facial_match_record),
            compliance_checks=[ComplianceCheckSchema.from_orm(check) for check in compliance_checks],
            notifications=[NotificationSchema.from_orm(notification)]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(f"{settings.API_V1_STR}/kyc/status/{customer_id}", response_model=KYCResponse)
async def get_kyc_status(customer_id: int):
    """
    Get the current status of a KYC verification process.
    """
    try:
        # In a real application, you would fetch this from the database
        # For this example, we'll return a mock response
        raise HTTPException(status_code=501, detail="Not implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(f"{settings.API_V1_STR}/kyc/review/{customer_id}")
async def review_kyc(customer_id: int, decision: str, comments: str = None):
    """
    Review and update the status of a KYC verification.
    """
    try:
        # In a real application, you would update the database here
        # For this example, we'll return a mock response
        raise HTTPException(status_code=501, detail="Not implemented")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 