import cv2
import time
from typing import Tuple, Optional
import numpy as np
from . import config
import logging

logger = logging.getLogger(__name__)

class SecurityCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(config.CAMERA_INDEX)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.first_frame = None
        self.last_motion_time = time.time()
        self.monitoring_active = False
        self.inactivity_start_time = None
        
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera."""
        return self.video.read()
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, Optional[np.ndarray], bool]:
        """Process frame for motion detection.
        Returns:
            - processed_frame: Frame with detection rectangles
            - motion_detected: Whether motion was detected
            - debug_frame: Frame showing motion detection data
            - should_capture: Whether this motion should trigger a capture
        """
        motion_detected = False
        should_capture = False
        processed_frame = frame.copy()
        current_time = time.time()
        
        # Convert to grayscale and apply Gaussian blur
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame_gau = cv2.GaussianBlur(gray_frame, config.GAUSSIAN_BLUR_SIZE, 0)
        
        # Initialize first frame if needed
        if self.first_frame is None:
            self.first_frame = gray_frame_gau
            return processed_frame, motion_detected, None, should_capture
            
        # Calculate frame difference
        delta_frame = cv2.absdiff(self.first_frame, gray_frame_gau)
        thresh_frame = cv2.threshold(delta_frame, config.MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]
        dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) < config.MIN_CONTOUR_AREA:
                continue
                
            motion_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(processed_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        # Update motion timing
        if motion_detected:
            self.last_motion_time = current_time
            if not self.monitoring_active:
                self.inactivity_start_time = None
        else:
            if self.inactivity_start_time is None:
                self.inactivity_start_time = current_time
        
        # Check if we should start monitoring
        if not self.monitoring_active:
            if (self.inactivity_start_time is not None and 
                current_time - self.inactivity_start_time >= config.INACTIVITY_TIMEOUT):
                logger.info("No motion for 30 minutes. Monitoring activated!")
                self.monitoring_active = True
        
        # Determine if we should capture this motion
        if motion_detected and self.monitoring_active:
            should_capture = True
            self.monitoring_active = False  # Reset monitoring after capture
            logger.info("Motion detected after inactivity period! Capturing image.")
            
        self.first_frame = gray_frame_gau
        return processed_frame, motion_detected, dil_frame, should_capture
        
    def release(self):
        """Release the camera resources."""
        self.video.release()
        cv2.destroyAllWindows()
