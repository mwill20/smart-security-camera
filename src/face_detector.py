import cv2
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self):
        # Load the pre-trained face cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
    def detect_faces(self, frame: np.ndarray) -> Tuple[List[Tuple[int, int, int, int]], np.ndarray]:
        """
        Detect faces in the frame and return their locations.
        Returns:
            - List of face coordinates (x, y, w, h)
            - Frame with face rectangles drawn
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        frame_with_faces = frame.copy()
        face_locations = []
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame_with_faces, (x, y), (x+w, y+h), (255, 0, 0), 2)
            face_locations.append((x, y, w, h))
            
        return face_locations, frame_with_faces
