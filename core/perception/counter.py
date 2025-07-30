import cv2
import numpy as np
import json
import os
from argparse import Namespace
from ultralytics import YOLO
import sys
import os
# Add ByteTrack to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ByteTrack')))
from yolox.tracker.byte_tracker import BYTETracker

class ZoneCounter:
    def __init__(self, config_path=None):
        self.model = YOLO("yolov8n.pt")
        self.tracker = self._init_tracker()
        
        # Default config path if none provided
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..", "configs", "zones", "intersection_a.json"
            )
        
        self.zones = self._load_zones(config_path)
        self.zone_counts = {zone: 0 for zone in self.zones}
        self.zone_visits = {zone: set() for zone in self.zones}

    def _init_tracker(self):
        args = Namespace(
            track_thresh=0.5,
            match_thresh=0.8,
            track_buffer=30,
            aspect_ratio_thresh=1.6,
            min_box_area=10,
            mot20=False
        )
        return BYTETracker(args)

    def _load_zones(self, config_path):
        try:
            with open(config_path) as f:
                zone_data = json.load(f)
                return {k: np.array(v, np.int32) for k, v in zone_data.items()}
        except FileNotFoundError:
            raise FileNotFoundError(f"Zone config file not found at: {config_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {config_path}")

    def detect_vehicles(self, frame):
        results = self.model(frame, verbose=False)[0]
        vehicle_boxes = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id in [2, 3, 5, 7]:  # car, motorcycle, bus, truck
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = float(box.conf[0])
                vehicle_boxes.append([x1, y1, x2, y2, conf])
        return np.array(vehicle_boxes, dtype=np.float32) if vehicle_boxes else np.empty((0, 5), dtype=np.float32)

    def update_counts(self, tracked_objs, frame_shape):
        for track in tracked_objs:
            x1, y1, w, h = map(int, track.tlwh)
            x2, y2 = x1 + w, y1 + h
            track_id = track.track_id

            for zone_name, polygon in self.zones.items():
                if self._is_in_zone((x1, y1, x2, y2), polygon) and track_id not in self.zone_visits[zone_name]:
                    self.zone_counts[zone_name] += 1
                    self.zone_visits[zone_name].add(track_id)

    def _is_in_zone(self, box, polygon):
        cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        return cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0

    def _visualize(self, frame, tracked_objs, display_size=(1280, 720)):
        for zone_name, poly in self.zones.items():
            cv2.polylines(frame, [poly], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.putText(frame, zone_name, tuple(poly[0]), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

        for track in tracked_objs:
            x1, y1, w, h = map(int, track.tlwh)
            x2, y2 = x1 + w, y1 + h
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(frame, f"ID {track.track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            for zone_name, polygon in self.zones.items():
                if track.track_id in self.zone_visits[zone_name]:
                    cv2.putText(frame, f"In {zone_name}", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        y_offset = 20
        for zone, count in self.zone_counts.items():
            cv2.putText(frame, f"{zone}: {count} vehicles", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            y_offset += 25

        frame = cv2.resize(frame, display_size)
        cv2.imshow("Smart Traffic Counter", frame)
        return frame

    def run(self, video_path, display=False, output_path=None):
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..", "data", "processed", "zone_counts.json"
            )

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {video_path}")

        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("Cannot read first frame.")
        frame_height, frame_width = frame.shape[:2]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.detect_vehicles(frame)
            tracked_objs = self.tracker.update(detections, [frame_height, frame_width], (frame_height, frame_width))
            self.update_counts(tracked_objs, (frame_height, frame_width))

            if display:
                self._visualize(frame, tracked_objs)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.zone_counts, f, indent=4)
        print(f"[INFO] Zone counts saved to {output_path}")
        return self.zone_counts

if __name__ == "__main__":
    try:
        counter = ZoneCounter()
        counter.run(
            video_path=os.path.join(
                os.path.dirname(__file__),
                "..", "..", "data", "raw", "rtvClip1.mp4"
            ),
            display=True
        )
    except Exception as e:
        print(f"[ERROR] {str(e)}")