import cv2
import time
import logging
from threading import Thread
from datetime import datetime
from src import config
from src.camera import SecurityCamera
from src.notifier_enhanced import EnhancedNotifier
from src.face_detector import FaceDetector
from src.scheduler import MonitoringSchedule
from src.web_interface import WebInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_folder():
    """Clean up old images."""
    import os
    import glob
    files = glob.glob(f"{config.IMAGES_DIR}/*")
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            logger.error(f"Error deleting {f}: {str(e)}")

def main():
    logger.info("Starting enhanced security camera system...")
    logger.info("System will start monitoring after 1 minute of inactivity")
    
    try:
        # Initialize components
        camera = SecurityCamera(max_retries=5)
        notifier = EnhancedNotifier()
        face_detector = FaceDetector()
        scheduler = MonitoringSchedule()
        
        # Initialize web interface if enabled
        if config.WEB_INTERFACE_ENABLED:
            web_interface = WebInterface(camera, scheduler)
            web_interface.run(host=config.WEB_HOST, port=config.WEB_PORT)
        
        count = 1
        last_direction = None
        last_position = None
        
        while True:
            # Check if we should be monitoring based on schedule
            if not scheduler.is_monitoring_time():
                time.sleep(60)  # Sleep for a minute if outside monitoring hours
                continue
                
            # Read and process frame
            check, frame = camera.read_frame()
            if not check:
                logger.error("Failed to read frame")
                break
                
            processed_frame, motion_detected, should_capture = camera.process_frame(frame)
            
            # Detect faces if enabled
            face_locations = []
            if config.FACE_DETECTION_ENABLED:
                face_locations, processed_frame = face_detector.detect_faces(processed_frame)
            
            # Handle motion detection and capture
            if should_capture:
                logger.info(f"Motion detected! Capturing {config.TOTAL_CAPTURES} images...")
                captured_images = []
                motion_positions = []
                
                # Capture series of images
                for i in range(config.TOTAL_CAPTURES):
                    image_path = f"{config.IMAGES_DIR}/{count}_{i+1}.png"
                    cv2.imwrite(image_path, processed_frame)
                    captured_images.append(image_path)
                    count += 1
                    
                    # Track motion direction
                    if face_locations:
                        x, y, w, h = face_locations[0]  # Use first face for tracking
                        center = (x + w//2, y + h//2)
                        motion_positions.append(center)
                    
                    # Wait for next frame
                    time.sleep(config.CAPTURE_INTERVAL)
                    check, frame = camera.read_frame()
                    if check:
                        processed_frame, _, _ = camera.process_frame(frame)
                        if config.FACE_DETECTION_ENABLED:
                            face_locations, processed_frame = face_detector.detect_faces(processed_frame)
                
                # Determine motion direction
                motion_direction = None
                if len(motion_positions) >= 2:
                    start_pos = motion_positions[0]
                    end_pos = motion_positions[-1]
                    dx = end_pos[0] - start_pos[0]
                    dy = end_pos[1] - start_pos[1]
                    
                    if abs(dx) > abs(dy):
                        motion_direction = "right" if dx > 0 else "left"
                    else:
                        motion_direction = "down" if dy > 0 else "up"
                
                # Select middle images to send
                if len(captured_images) >= config.TOTAL_CAPTURES:
                    start_idx = (config.TOTAL_CAPTURES - config.IMAGES_TO_SEND) // 2
                    end_idx = start_idx + config.IMAGES_TO_SEND
                    images_to_send = captured_images[start_idx:end_idx]
                    
                    # Send notification
                    try:
                        notifier.send_notification(
                            images_to_send,
                            face_detected=bool(face_locations),
                            motion_direction=motion_direction
                        )
                        # Start cleanup thread
                        clean_thread = Thread(target=clean_folder)
                        clean_thread.daemon = True
                        clean_thread.start()
                    except Exception as e:
                        logger.error(f"Failed to send notification: {str(e)}")
            
            # Display frames
            status_text = "MONITORING" if camera.monitoring_active else "WAITING FOR INACTIVITY"
            status_color = (0, 255, 0) if camera.monitoring_active else (0, 0, 255)
            
            # Add status text to frame
            cv2.putText(processed_frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            
            # Add timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(processed_frame, timestamp, (10, processed_frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Show frames
            cv2.imshow("Security Feed", processed_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        
    finally:
        logger.info("Cleaning up...")
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
