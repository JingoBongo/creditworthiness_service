import cv2
import os

# Load the video file
video_path = "path/to/video/file.mp4"
cap = cv2.VideoCapture(video_path)

# Create a Haar Cascade classifier to detect faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Initialize variables
count = 0
frame_count = 0

# Loop through the video frames
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        frame_count += 1

        # Only process every 100th frame
        if frame_count % 100 == 0:

            # Convert the frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),
                                                  flags=cv2.CASCADE_SCALE_IMAGE)

            # If faces are detected, save them as images
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    crop_img = frame[y:y + h, x:x + w]
                    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)  # Convert to RGB
                    cv2.imwrite(os.path.join('path/to/save/faces', f"face_{count}.jpg"), crop_img)
                    count += 1
    else:
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()