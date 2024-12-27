import cv2
import time
from email_me import send_email

video = cv2.VideoCapture(0)
time.sleep(0.1)  # Short delay for camera initialization

first_frame = None
status_list = []

while True:
    status = 0
    check, frame = video.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and detail
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Initialize first frame or update continuously
    if first_frame is None:
        first_frame = gray_frame_gau
        continue

    # Calculate difference between current frame and first frame
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # Apply thresholding to isolate significant differences
    thresh_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Find contours of the thresholded frame
    contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw rectangles around significant contours
    for contour in contours:
        if cv2.contourArea(contour) < 3000:  # Adjust contour area for sensitivity
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        send_email()


    # Display the processed video feed
    cv2.imshow("Motion Detection", frame)

    # Update the first frame to current for next iteration
    first_frame = gray_frame_gau

    # Break loop if 'q' is pressed
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

# Release the camera and close OpenCV windows
video.release()
cv2.destroyAllWindows()