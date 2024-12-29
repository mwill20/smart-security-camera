import cv2
import time
import os
import glob
from threading import Thread
import logging
from src.camera import SecurityCamera
from src.notifier import EmailNotifier
from src import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_folder():
    """Clean up old images."""
    logger.info("Cleaning up old images...")
    images = glob.glob(f"{config.IMAGES_DIR}/*.png")
    for image in images:
        os.remove(image)
    logger.info("Cleanup complete")

def main():
    logger.info("Starting security camera system...")
    logger.info("System will start monitoring after 30 minutes of inactivity")
    
    # Initialize camera and notifier
    camera = SecurityCamera()
    notifier = EmailNotifier()
    count = 1
    
    try:
        while True:
            # Read and process frame
            check, frame = camera.read_frame()
            if not check:
                logger.error("Failed to read frame from camera")
                break
                
            processed_frame, motion_detected, debug_frame, should_capture = camera.process_frame(frame)
            
            # Handle motion detection and capture
            if should_capture:
                image_path = f"{config.IMAGES_DIR}/{count}.png"
                cv2.imwrite(image_path, processed_frame)
                count += 1
                
                # Send notification
                try:
                    notifier.send_notification(image_path)
                    # Start cleanup thread
                    clean_thread = Thread(target=clean_folder)
                    clean_thread.daemon = True
                    clean_thread.start()
                except Exception as e:
                    logger.error(f"Failed to send notification: {str(e)}")
            
            # Display frames
            status_text = "MONITORING" if camera.monitoring_active else "WAITING FOR INACTIVITY"
            cv2.putText(
                processed_frame,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0) if camera.monitoring_active else (0, 0, 255),
                2
            )
            
            cv2.imshow("Security Feed", processed_frame)
            if debug_frame is not None:
                cv2.imshow("Motion Detection", debug_frame)
            
            # Check for quit command
            if cv2.waitKey(config.MOTION_CHECK_INTERVAL) & 0xFF == ord('q'):
                logger.info("Quit command received")
                break
                
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        
    finally:
        # Cleanup
        camera.release()
        clean_folder()
        logger.info("Security camera system shutdown complete")

if __name__ == "__main__":
    main()
