import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Camera Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Motion Detection Configuration
MOTION_THRESHOLD = 60
MIN_CONTOUR_AREA = 3000
GAUSSIAN_BLUR_SIZE = (21, 21)
INACTIVITY_TIMEOUT = 60  # 1 minute in seconds
MOTION_CHECK_INTERVAL = 1  # Check for motion every 1 second

# Capture Configuration
TOTAL_CAPTURES = 10  # Total number of images to capture
CAPTURE_INTERVAL = 1  # Seconds between captures
IMAGES_TO_SEND = 4  # Number of middle images to send

# Face Detection Configuration
FACE_DETECTION_ENABLED = True
MIN_FACE_SIZE = (30, 30)
FACE_DETECTION_SCALE = 1.1
FACE_DETECTION_NEIGHBORS = 5

# Monitoring Schedule Configuration
DEFAULT_START_TIME = "00:00"  # 24-hour format
DEFAULT_END_TIME = "23:59"
DAY_SENSITIVITY = 3000
NIGHT_SENSITIVITY = 2000

# Image Storage Configuration
IMAGES_DIR = "images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Optional SMS Configuration (Twilio)
TWILIO_ENABLED = False
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_FROM = os.getenv('TWILIO_PHONE_FROM')
TWILIO_PHONE_TO = os.getenv('TWILIO_PHONE_TO')

# Web Interface Configuration
WEB_INTERFACE_ENABLED = True
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
