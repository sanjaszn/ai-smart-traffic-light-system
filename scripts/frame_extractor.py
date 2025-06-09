import os
import cv2

# Dynamically get project root
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # goes up from /scripts

# Paths
video_path = os.path.join(base_dir, "data", "raw", "trafficVid.mp4")
output_folder = os.path.join(base_dir, "data", "processed", "frames")

# Frame saving interval
frame_interval = 10  # Save every 10th frame

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Cannot open video at {video_path}")
    exit()

frame_id = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_id % frame_interval == 0:
        filename = os.path.join(output_folder, f"frame_{frame_id:04d}.jpg")
        cv2.imwrite(filename, frame)
        saved_count += 1

    frame_id += 1

cap.release()
print(f"✅ Done! Saved {saved_count} frames in '{output_folder}'")
