from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from typing import Dict, Any, Optional, List
from ...core.config import settings

class Notifier:
    def __init__(self):
        # Initialize SendGrid client
        self.sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        
        # Initialize Twilio client
        self.twilio_client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    def send_email(self, to_email: str, subject: str, content: str) -> Dict[str, Any]:
        """
        Send an email using SendGrid.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email content (HTML)
            
        Returns:
            Dictionary containing email sending results
        """
        try:
            message = Mail(
                from_email='noreply@kyc-automation.com',
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            
            response = self.sg.send(message)
            
            return {
                'status': 'sent',
                'message_id': response.headers.get('X-Message-Id'),
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Send an SMS using Twilio.
        
        Args:
            to_phone: Recipient phone number
            message: SMS content
            
        Returns:
            Dictionary containing SMS sending results
        """
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_='+1234567890',  # Replace with your Twilio phone number
                to=to_phone
            )
            
            return {
                'status': 'sent',
                'message_id': message.sid,
                'status_code': message.status
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def send_kyc_approval_notification(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send KYC approval notification via email and SMS.
        
        Args:
            customer_data: Dictionary containing customer information
            
        Returns:
            Dictionary containing notification results
        """
        try:
            # Prepare email content
            email_subject = "Your KYC Verification is Complete"
            email_content = f"""
            <html>
                <body>
                    <h1>KYC Verification Complete</h1>
                    <p>Dear {customer_data['first_name']} {customer_data['last_name']},</p>
                    <p>We are pleased to inform you that your KYC verification has been completed successfully.</p>
                    <p>You can now proceed with using our services.</p>
                    <p>Best regards,<br>KYC Automation Team</p>
                </body>
            </html>
            """
            
            # Prepare SMS content
            sms_content = f"Dear {customer_data['first_name']}, your KYC verification is complete. You can now use our services."
            
            # Send notifications
            email_result = self.send_email(customer_data['email'], email_subject, email_content)
            sms_result = self.send_sms(customer_data['phone'], sms_content)
            
            return {
                'email': email_result,
                'sms': sms_result
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def send_kyc_rejection_notification(self, customer_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Send KYC rejection notification via email and SMS.
        
        Args:
            customer_data: Dictionary containing customer information
            reason: Reason for rejection
            
        Returns:
            Dictionary containing notification results
        """
        try:
            # Prepare email content
            email_subject = "KYC Verification Update"
            email_content = f"""
            <html>
                <body>
                    <h1>KYC Verification Update</h1>
                    <p>Dear {customer_data['first_name']} {customer_data['last_name']},</p>
                    <p>We regret to inform you that your KYC verification could not be completed at this time.</p>
                    <p>Reason: {reason}</p>
                    <p>Please contact our support team for further assistance.</p>
                    <p>Best regards,<br>KYC Automation Team</p>
                </body>
            </html>
            """
            
            # Prepare SMS content
            sms_content = f"Dear {customer_data['first_name']}, your KYC verification requires attention. Please check your email for details."
            
            # Send notifications
            email_result = self.send_email(customer_data['email'], email_subject, email_content)
            sms_result = self.send_sms(customer_data['phone'], sms_content)
            
            return {
                'email': email_result,
                'sms': sms_result
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }

    def send_kyc_review_notification(self, customer_data: Dict[str, Any], required_actions: List[str]) -> Dict[str, Any]:
        """
        Send KYC review notification via email and SMS.
        
        Args:
            customer_data: Dictionary containing customer information
            required_actions: List of actions required from the customer
            
        Returns:
            Dictionary containing notification results
        """
        try:
            # Prepare email content
            email_subject = "Additional Information Required for KYC Verification"
            actions_list = "\n".join([f"<li>{action}</li>" for action in required_actions])
            email_content = f"""
            <html>
                <body>
                    <h1>Additional Information Required</h1>
                    <p>Dear {customer_data['first_name']} {customer_data['last_name']},</p>
                    <p>We need some additional information to complete your KYC verification:</p>
                    <ul>
                        {actions_list}
                    </ul>
                    <p>Please provide the requested information at your earliest convenience.</p>
                    <p>Best regards,<br>KYC Automation Team</p>
                </body>
            </html>
            """
            
            # Prepare SMS content
            sms_content = f"Dear {customer_data['first_name']}, additional information is required for your KYC verification. Please check your email."
            
            # Send notifications
            email_result = self.send_email(customer_data['email'], email_subject, email_content)
            sms_result = self.send_sms(customer_data['phone'], sms_content)
            
            return {
                'email': email_result,
                'sms': sms_result
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            } 