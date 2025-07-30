#!/usr/bin/env python3
"""Data Processing Module for Traffic Light System"""
import cv2
import json
import random
import time
import sys
import os
from pathlib import Path
from threading import Thread, Lock
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.perception.counter import ZoneCounter
from core.utils.mock_zone_generator import MockZoneGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
UPDATE_INTERVALS = {
    'video_processing': 2.0,
    'mock_generator': 30.0,
}

ZONE_MAPPING = {
    "Zone A": "South",
    "Zone B": "East", 
    "Zone C": "North",
    "Zone D": "West"
}

# Thread-safe file access
file_lock = Lock()

def map_counts(zone_counts: Dict[str, int]) -> Dict[str, int]:
    """Map zone counts to simulation directions"""
    return {ZONE_MAPPING[k]: v for k, v in zone_counts.items()}

def safe_write_counts(filepath: Path, data: Dict):
    """Thread-safe writing of zone counts"""
    with file_lock:
        temp_file = filepath.with_suffix('.tmp')
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            temp_file.replace(filepath)
        except Exception as e:
            logger.error(f"Failed to write counts: {e}")
            if temp_file.exists():
                temp_file.unlink()

def safe_read_counts(filepath: Path) -> Optional[Dict]:
    """Thread-safe reading of zone counts"""
    with file_lock:
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

class VideoProcessor:
    """Handles video processing and vehicle detection"""
    
    def __init__(self, video_path: str, data_file: str):
        self.video_path = Path(video_path)
        self.data_file = Path(data_file)
        self.counter = ZoneCounter()
        self.last_update = 0
        
    def process_video(self):
        """Process video and update zone counts"""
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {self.video_path}")
            return
            
        try:
            while True:
                current_time = time.time()
                if current_time - self.last_update < UPDATE_INTERVALS['video_processing']:
                    time.sleep(0.1)
                    continue
                    
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                    
                try:
                    detections = self.counter.detect_vehicles(frame)
                    tracked = self.counter.tracker.update(
                        detections, 
                        [frame.shape[0], frame.shape[1]], 
                        (frame.shape[0], frame.shape[1])
                    )
                    self.counter.update_counts(tracked, frame.shape)
                    safe_write_counts(self.data_file, self.counter.zone_counts)
                    self.last_update = current_time
                except Exception as e:
                    logger.error(f"Video processing error: {e}")
        finally:
            cap.release()

class MockDataProcessor:
    """Handles mock data generation"""
    
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.generator = MockZoneGenerator(str(data_file), UPDATE_INTERVALS['mock_generator'])
        
    def generate_mock_data(self):
        """Generate and write mock traffic data"""
        while True:
            try:
                counts = self.generator.generate_counts()
                safe_write_counts(self.data_file, counts)
                time.sleep(UPDATE_INTERVALS['mock_generator'])
            except Exception as e:
                logger.error(f"Mock generator error: {e}")

class DataProcessor:
    """Main data processor that coordinates video and mock data"""
    
    def __init__(self, video_path: str, data_file: str):
        self.video_path = Path(video_path)
        self.data_file = Path(data_file)
        self.video_processor = VideoProcessor(str(video_path), data_file)
        self.mock_processor = MockDataProcessor(data_file)
        
    def start_processing(self):
        """Start appropriate data processing based on available video"""
        # Ensure data directory exists
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with empty counts
        safe_write_counts(self.data_file, {k: 0 for k in ZONE_MAPPING.keys()})
        
        # Start appropriate data source
        if self.video_path.exists():
            logger.info(f"Starting video processing with {self.video_path}")
            Thread(target=self.video_processor.process_video, daemon=True).start()
        else:
            logger.warning(f"Video not found at {self.video_path}, using mock data")
            Thread(target=self.mock_processor.generate_mock_data, daemon=True).start()
    
    def get_current_counts(self) -> Optional[Dict[str, int]]:
        """Get current zone counts"""
        return safe_read_counts(self.data_file) 