"""
Send email reports
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

class EmailSender:
    """Send email reports"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.username = os.getenv('EMAIL_USER', '')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        self.enabled = bool(self.username and self.password)
    
    def send_report(self, to_emails: list, subject: str, body: str, attachments: list = None):
        """Send email with report"""
        if not self.enabled:
            logger.warning("Email not configured, skipping send")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={Path(file_path).name}'
                            )
                            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Email send failed: {str(e)}")
            return False