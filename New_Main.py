import cv2
import time
import os
import glob
from email_me import send_email
from threading import Thread

# Initialize video capture and delay
video = cv2.VideoCapture(0)
time.sleep(0.1)  # Short delay for camera initialization

first_frame = None
status_list = []
count = 1

def clean_folder():
    print("clean_folder function started")
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)
    print("clean_function fuction ended")

# Ensure the images directory exists
images_dir = "images"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

while True:
    status = 0
    check, frame = video.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Initialize first frame
    if first_frame is None:
        first_frame = gray_frame_gau
        continue

    # Calculate frame difference
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # Apply threshold and dilation
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Display the thresholded video
    cv2.imshow("My video", dil_frame)

    # Find contours and draw rectangles
    contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 3000:  # Filter small contours
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            image_path = f"{images_dir}/{count}.png"
            cv2.imwrite(image_path, frame)
            count += 1
            all_images = glob.glob(f"{images_dir}/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(target=send_email, args=(image_with_object, ))
        email_thread.daemon = True
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()


    # Display the video with detection
    cv2.imshow("Motion Detection", frame)
    first_frame = gray_frame_gau

    # Exit on 'q' key press
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

# Release resources
video.release()
clean_thread.start()
cv2.destroyAllWindows()
