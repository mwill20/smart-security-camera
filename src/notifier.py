import smtplib
import mimetypes
from email.message import EmailMessage
from . import config
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.sender = config.EMAIL_SENDER
        self.receiver = config.EMAIL_RECEIVER
        self.password = config.EMAIL_PASSWORD
        
    def send_notification(self, image_paths: List[str]):
        """Send email notification with multiple captured images."""
        try:
            logger.info(f"Preparing email notification with {len(image_paths)} images...")
            email_message = EmailMessage()
            email_message["Subject"] = "Security Alert: Motion Detected!"
            email_message["From"] = self.sender
            email_message["To"] = self.receiver
            email_message.set_content(
                "Motion was detected by your security camera.\n"
                f"Attached are {len(image_paths)} images captured during the event."
            )
            
            # Attach images
            for idx, image_path in enumerate(image_paths, 1):
                mime_type, _ = mimetypes.guess_type(image_path)
                mime_type = mime_type or 'application/octet-stream'
                mime_maintype, mime_subtype = mime_type.split('/')
                
                with open(image_path, "rb") as file:
                    content = file.read()
                email_message.add_attachment(
                    content,
                    maintype=mime_maintype,
                    subtype=mime_subtype,
                    filename=f"motion_detected_{idx}.png"
                )
            
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(email_message)
                
            logger.info("Email notification sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            raise
