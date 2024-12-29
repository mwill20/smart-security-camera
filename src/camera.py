import cv2
from typing import Tuple, Optional
import numpy as np
from . import config

class SecurityCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(config.CAMERA_INDEX)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        self.first_frame = None
        
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Read a frame from the camera."""
        return self.video.read()
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, bool, Optional[np.ndarray]]:
        """Process frame for motion detection."""
        motion_detected = False
        processed_frame = frame.copy()
        
        # Convert to grayscale and apply Gaussian blur
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_frame_gau = cv2.GaussianBlur(gray_frame, config.GAUSSIAN_BLUR_SIZE, 0)
        
        # Initialize first frame if needed
        if self.first_frame is None:
            self.first_frame = gray_frame_gau
            return processed_frame, motion_detected, None
            
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
            
        self.first_frame = gray_frame_gau
        return processed_frame, motion_detected, dil_frame
        
    def release(self):
        """Release the camera resources."""
        self.video.release()
        cv2.destroyAllWindows()
