from ultralytics import YOLO
import os

# Load a pre-trained YOLOv8 model (you can use 'yolov8n', 'yolov8s', etc.)
model = YOLO('yolov8n.pt')  # 'n' = nano, fastest/smallest

# Path to your frames
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frames_path = os.path.join(base_dir, 'data', 'processed', 'frames')
output_path = os.path.join(base_dir, 'data', 'processed', 'yolo_output')

os.makedirs(output_path, exist_ok=True)

# Run detection on all frames
results = model.predict(source=frames_path, save=True, project=output_path, name='detect', exist_ok=True)

print("✅ YOLO detection done. Check 'yolo_output/detect'")
