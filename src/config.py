import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email Configuration
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Camera Configuration
CAMERA_INDEX = 0  # Default webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Motion Detection Configuration
MOTION_THRESHOLD = 60
MIN_CONTOUR_AREA = 3000
GAUSSIAN_BLUR_SIZE = (21, 21)
INACTIVITY_TIMEOUT = 1800  # 30 minutes in seconds
MOTION_CHECK_INTERVAL = 1  # Check for motion every 1 second

# Image Storage Configuration
IMAGES_DIR = "images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)
