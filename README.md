# 🚦 Smart AI-Powered Traffic Light System (Nairobi Prototype)

An AI-driven system designed to analyze real-world traffic from video and simulate adaptive traffic light control — starting with Nairobi's most chaotic intersections.

> Built for scalability, experimentation, and real-time decision-making using modern computer vision and tracking techniques.

---

## 🎯 Core Goals

- Replace static timers with intelligent light control
- Use real-world data (video) to simulate behavior
- Design modular tools to support custom experiments
- Prioritize simplicity, clarity, and extendability

---

## ✅ Current Capabilities

- 🎥 Load and process traffic videos frame-by-frame
- 🧠 Detect vehicles with YOLOv8
- 🎯 Multi-zone, polygon-based detection (user-drawn)
- 🔁 Multi-object tracking with ByteTrack
- 📊 Vehicle counting per zone
- 🛠️ Tools for drawing zones, extracting frames, and simulating
- 🧮 More accurate counting: use center-point logic to reduce double-counting  
---

## 🚧 Next Milestones
- 🚘 Classify vehicle types (e.g., car, bus, bike) using YOLOv8 class labels
  
- 🌍 Integrate real-time counts into the Pygame simulation (Step 2C) for adaptive light decisions

- 🚦 Implement basic smart light control logic based on dynamic zone counts

- 🧪 Improve simulation realism: Add animated vehicles + signal transitions

- 📉 Measure per-zone congestion using vehicle density, wait time, and inflow/outflow rates

- 🧠 Train & compare RL agents for signal optimization (vs. hard-coded logic)

- 📊 Design a lightweight dashboard for traffic state visualization & system control

- ☁️ Prepare for cloud/offline deployment with modular zone config + input/output decoupling
---

## 🧰 Tech Stack

- **Python 3.12**
- **YOLOv8 (Ultralytics)**
- **ByteTrack**
- OpenCV, NumPy, Matplotlib
- Git, GitHub, VS Code

---

## 🗂️ Project Structure (Simplified)

trafficAI/
├── data/
│ ├── raw/ # Input videos
│ └── processed/ # Frames, detections, yolo_output
├── scripts/ # Core logic modules
│ ├── detect_vehicles.py # YOLO-based detection
│ ├── zone_counter_bytetrack.py # Counting + tracking
│ ├── frame_extractor.py # Frame grabbing
│ ├── multi_zone_drawer.py # Polygon zone UI
│ ├── stabilize_video.py # Frame stabilization
│ └── play_video.py # Simple playback tool
├── smart_traffic_ai/
│ └── main.py # Entrypoint for pipeline orchestration
├── yolov8n.pt # YOLOv8 model weights
├── requirements.txt
├── README.md

yaml
Copy
Edit

🗃️ *Old or experimental logic (Kalman, SORT, etc.) lives in `_archive_unused/` — useful for future experiments.*

---

## 🚫 What’s Not in This Repo

> To keep the repo clean and focused, these are excluded via `.gitignore`:

- Large video files (`.mp4`, `.avi`, etc.)
- Virtual environments (`.venv/`)
- Model weights (`.pt`)
- Cache files (`__pycache__/`)
- Outputs, logs, and temporary data

---

## 🧠 Philosophy

- Modular code = better experiments  
- Real-world video > synthetic data  
- No black boxes: everything visible, editable, traceable  
- Simplicity > cleverness

---

## 👤 Author

**Sanja Timothy**  
Computer Science student – Nairobi, Kenya  
💡 Focused on deployable, scalable AI systems for real-world impact.

---

## ⚙️ Running This Project

> You’ll need to:

1. Set up a Python virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
