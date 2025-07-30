#!/usr/bin/env python3
"""YOLOv8 Vehicle Detector Module"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional

class VehicleDetector:
    """YOLOv8-based vehicle detection with ONNX optimization"""
    
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """
        Initialize YOLOv8 detector
        
        Args:
            model_path: Path to YOLOv8 model weights
            conf_threshold: Confidence threshold for detections
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        
        # Vehicle class IDs in COCO dataset
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck'
        }
    
    def detect_vehicles(self, frame: np.ndarray) -> np.ndarray:
        """
        Detect vehicles in frame
        
        Args:
            frame: Input image/frame (BGR format)
            
        Returns:
            detections: Array of [x1, y1, x2, y2, confidence] for vehicles
        """
        try:
            # Run YOLOv8 inference
            results = self.model(frame, verbose=False)[0]
            
            vehicle_boxes = []
            for box in results.boxes:
                cls_id = int(box.cls[0])
                
                # Only process vehicle classes
                if cls_id in self.vehicle_classes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    
                    # Apply confidence threshold
                    if conf >= self.conf_threshold:
                        vehicle_boxes.append([x1, y1, x2, y2, conf])
            
            return np.array(vehicle_boxes, dtype=np.float32) if vehicle_boxes else np.empty((0, 5), dtype=np.float32)
            
        except Exception as e:
            print(f"Detection error: {e}")
            return np.empty((0, 5), dtype=np.float32)
    
    def get_detection_stats(self, frame: np.ndarray) -> dict:
        """
        Get detection statistics for monitoring
        
        Args:
            frame: Input frame
            
        Returns:
            stats: Dictionary with detection statistics
        """
        detections = self.detect_vehicles(frame)
        
        stats = {
            'total_detections': len(detections),
            'avg_confidence': float(np.mean(detections[:, 4])) if len(detections) > 0 else 0.0,
            'detection_areas': []
        }
        
        # Calculate detection areas
        for det in detections:
            x1, y1, x2, y2 = det[:4]
            area = (x2 - x1) * (y2 - y1)
            stats['detection_areas'].append(area)
        
        return stats 