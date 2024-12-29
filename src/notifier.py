import smtplib
import imghdr
from email.message import EmailMessage
from . import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self):
        self.sender = config.EMAIL_SENDER
        self.receiver = config.EMAIL_RECEIVER
        self.password = config.EMAIL_PASSWORD
        
    def send_notification(self, image_path: str):
        """Send email notification with the captured image."""
        try:
            logger.info("Preparing email notification...")
            email_message = EmailMessage()
            email_message["Subject"] = "Security Alert: Motion Detected!"
            email_message["From"] = self.sender
            email_message["To"] = self.receiver
            email_message.set_content(
                "Motion was detected by your security camera.\n"
                "Please find the captured image attached."
            )
            
            # Attach image
            with open(image_path, "rb") as file:
                content = file.read()
            email_message.add_attachment(
                content,
                maintype="image",
                subtype=imghdr.what(None, content)
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
