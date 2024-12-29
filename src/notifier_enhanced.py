import smtplib
import mimetypes
from email.message import EmailMessage
from twilio.rest import Client
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import os
from typing import List, Optional
import logging
from . import config

logger = logging.getLogger(__name__)

class EnhancedNotifier:
    def __init__(self):
        self.email_sender = config.EMAIL_SENDER
        self.email_receiver = config.EMAIL_RECEIVER
        self.email_password = config.EMAIL_PASSWORD
        
        # Twilio setup (optional)
        self.twilio_client = None
        if hasattr(config, 'TWILIO_ACCOUNT_SID') and hasattr(config, 'TWILIO_AUTH_TOKEN'):
            self.twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            
    def add_timestamp(self, image: np.ndarray) -> np.ndarray:
        """Add timestamp to image."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        # Position timestamp at bottom-right
        w, h = img_pil.size
        text_size = 20
        try:
            font = ImageFont.truetype("arial.ttf", text_size)
        except:
            font = ImageFont.load_default()
            
        # Add semi-transparent background for timestamp
        text_bbox = draw.textbbox((0, 0), timestamp, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        margin = 10
        rect_coords = [
            w - text_width - margin * 2,
            h - text_height - margin * 2,
            w - margin,
            h - margin
        ]
        draw.rectangle(rect_coords, fill=(0, 0, 0, 128))
        
        # Draw timestamp
        draw.text(
            (w - text_width - margin, h - text_height - margin),
            timestamp,
            font=font,
            fill=(255, 255, 255)
        )
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
    def send_notification(self, image_paths: List[str], face_detected: bool = False,
                         motion_direction: Optional[str] = None):
        """Send enhanced notification with multiple images and detection details."""
        try:
            # Prepare email
            email_message = EmailMessage()
            email_message["Subject"] = f"Security Alert: {'Face' if face_detected else 'Motion'} Detected!"
            email_message["From"] = self.email_sender
            email_message["To"] = self.email_receiver
            
            # Create detailed message
            content = [
                "Security Alert Details:",
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Detection Type: {'Face Detected' if face_detected else 'Motion Detected'}",
            ]
            
            if motion_direction:
                content.append(f"Movement Direction: {motion_direction}")
                
            content.append(f"\nAttached are {len(image_paths)} images captured during the event.")
            
            email_message.set_content("\n".join(content))
            
            # Attach images with timestamps
            for idx, image_path in enumerate(image_paths, 1):
                # Read image and add timestamp
                image = cv2.imread(image_path)
                if image is not None:
                    image_with_timestamp = self.add_timestamp(image)
                    temp_path = f"{os.path.splitext(image_path)[0]}_timestamped.png"
                    cv2.imwrite(temp_path, image_with_timestamp)
                    
                    mime_type, _ = mimetypes.guess_type(temp_path)
                    mime_type = mime_type or 'application/octet-stream'
                    mime_maintype, mime_subtype = mime_type.split('/')
                    
                    with open(temp_path, "rb") as file:
                        content = file.read()
                    email_message.add_attachment(
                        content,
                        maintype=mime_maintype,
                        subtype=mime_subtype,
                        filename=f"detection_{idx}.png"
                    )
                    
                    # Clean up temporary file
                    os.remove(temp_path)
            
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(email_message)
                
            logger.info("Enhanced email notification sent successfully")
            
            # Send SMS if Twilio is configured
            if self.twilio_client and hasattr(config, 'TWILIO_PHONE_FROM') and hasattr(config, 'TWILIO_PHONE_TO'):
                sms_message = (
                    f"Security Alert: {'Face' if face_detected else 'Motion'} detected at "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
                    "Check your email for images."
                )
                self.twilio_client.messages.create(
                    body=sms_message,
                    from_=config.TWILIO_PHONE_FROM,
                    to=config.TWILIO_PHONE_TO
                )
                logger.info("SMS notification sent successfully")
                
        except Exception as e:
            logger.error(f"Failed to send enhanced notification: {str(e)}")
            raise
