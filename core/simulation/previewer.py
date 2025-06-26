import os
import cv2

# Get the base project directory
base_dir = os.path.dirname(os.path.abspath(__file__))  # current file location
video_path = os.path.join(base_dir, "data", "raw", "trafficVid.mp4")  # adjust path as needed

# Open the video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video at {video_path}")
else:
    print("Video opened successfully.")

# Read and display frames
frame_count = 0
while True:
    ret, frame = cap.read()

    if not ret:
        print("End of video or error reading frame.")
        break

    # Resize for viewing (optional)
    frame = cv2.resize(frame, (640, 480))

    # Show the frame
    cv2.imshow("Traffic Video Frame", frame)

    # Wait for 25ms and break if 'q' is pressed
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    frame_count += 1

print(f"Displayed {frame_count} frames.")

# Release video
cap.release()
cv2.destroyAllWindows()
