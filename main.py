import cv2
import time
import os
import glob
from threading import Thread
import logging
from src.camera import SecurityCamera
from src.notifier import EmailNotifier
from src import config

logging.basicConfig(level=logging.INFO)
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
    
    # Initialize camera and notifier
    camera = SecurityCamera()
    notifier = EmailNotifier()
    count = 1
    status_list = []
    
    try:
        while True:
            # Read and process frame
            check, frame = camera.read_frame()
            if not check:
                logger.error("Failed to read frame from camera")
                break
                
            processed_frame, motion_detected, debug_frame = camera.process_frame(frame)
            
            # Update status list
            status_list.append(1 if motion_detected else 0)
            status_list = status_list[-2:]  # Keep only last 2 states
            
            # Handle motion detection
            if motion_detected:
                image_path = f"{config.IMAGES_DIR}/{count}.png"
                cv2.imwrite(image_path, processed_frame)
                count += 1
                
                # Send email notification when motion stops
                if len(status_list) >= 2 and status_list[0] == 1 and status_list[1] == 0:
                    all_images = glob.glob(f"{config.IMAGES_DIR}/*.png")
                    if all_images:
                        index = int(len(all_images) / 2)
                        image_with_object = all_images[index]
                        
                        # Start notification and cleanup threads
                        email_thread = Thread(target=notifier.send_notification, args=(image_with_object,))
                        clean_thread = Thread(target=clean_folder)
                        
                        email_thread.start()
                        clean_thread.start()
            
            # Display frames
            cv2.imshow("Security Feed", processed_frame)
            if debug_frame is not None:
                cv2.imshow("Motion Detection", debug_frame)
            
            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
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
