import boto3
import pytesseract
from PIL import Image
import io
from typing import Dict, Any, Optional, List
from ...core.config import settings

class TextExtractor:
    def __init__(self):
        if settings.USE_AWS_TEXTRACT:
            self.client = boto3.client(
                'textract',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        else:
            self.client = None

    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from an image using either AWS Textract or Tesseract OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        if settings.USE_AWS_TEXTRACT and self.client:
            return self._extract_with_textract(image_path)
        else:
            return self._extract_with_tesseract(image_path)

    def _extract_with_textract(self, image_path: str) -> Dict[str, Any]:
        """Extract text using AWS Textract."""
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.client.analyze_document(
                Document={'Bytes': image_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            extracted_data = {
                'text': '',
                'key_value_pairs': {},
                'tables': []
            }
            
            # Extract text and key-value pairs
            for block in response.get('Blocks', []):
                if block['BlockType'] == 'LINE':
                    extracted_data['text'] += block['Text'] + '\n'
                elif block['BlockType'] == 'KEY_VALUE_SET':
                    if block['EntityTypes'] == ['KEY']:
                        key = block['Text']
                        value = self._find_value_for_key(block, response['Blocks'])
                        extracted_data['key_value_pairs'][key] = value
            
            return extracted_data
            
        except Exception as e:
            raise Exception(f"Error extracting text with Textract: {str(e)}")

    def _extract_with_tesseract(self, image_path: str) -> Dict[str, Any]:
        """Extract text using Tesseract OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            return {
                'text': text,
                'key_value_pairs': {},
                'tables': []
            }
            
        except Exception as e:
            raise Exception(f"Error extracting text with Tesseract: {str(e)}")

    def _find_value_for_key(self, key_block: Dict, blocks: List[Dict]) -> Optional[str]:
        """Helper method to find the value associated with a key in Textract response."""
        for relationship in key_block.get('Relationships', []):
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = next(
                        (block for block in blocks if block['Id'] == value_id),
                        None
                    )
                    if value_block:
                        return value_block.get('Text')
        return None 