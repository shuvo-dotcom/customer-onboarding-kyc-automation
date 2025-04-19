# KYC Automation Agent

A comprehensive Know Your Customer (KYC) automation system that handles document processing, facial recognition, and compliance checks.

## Features

- 📄 **OCR & Text Extraction**: Convert scanned documents to machine-readable text using Amazon Textract and Tesseract OCR
- 🗂️ **Document Classification**: ML-powered document type classification
- 👤 **Facial Recognition**: Match selfies with ID document photos
- 🕵️‍♂️ **Sanctions & PEP Checks**: Integration with compliance databases
- 🔄 **Workflow Automation**: Orchestrated processing pipeline
- 📢 **Notification System**: Automated customer communications
- 🧑‍💻 **Review Interface**: Web-based dashboard for compliance officers
- 🔁 **Continuous Learning**: Feedback loop for system improvement

## Project Structure

```
kyc_automation/
├── app/
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Core configuration and settings
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic models
│   ├── services/      # Business logic
│   │   ├── ocr/       # OCR processing
│   │   ├── ml/        # Machine learning models
│   │   ├── facial/    # Facial recognition
│   │   ├── compliance/# Compliance checks
│   │   └── notification/ # Notification system
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── alembic/           # Database migrations
└── scripts/           # Utility scripts
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

## Configuration

The system requires the following environment variables:

- `AWS_ACCESS_KEY_ID`: AWS credentials for Textract
- `AWS_SECRET_ACCESS_KEY`: AWS credentials for Textract
- `COMPLYADVANTAGE_API_KEY`: API key for compliance checks
- `TWILIO_ACCOUNT_SID`: Twilio credentials for SMS
- `TWILIO_AUTH_TOKEN`: Twilio credentials for SMS
- `SENDGRID_API_KEY`: SendGrid API key for emails
- `DATABASE_URL`: PostgreSQL connection string

## API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.