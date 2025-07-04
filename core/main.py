#!/usr/bin/env python3
"""Optimized AI Traffic Light System Pipeline"""
import cv2
import numpy as np
from contextlib import contextmanager
from typing import Dict, Any
from pathlib import Path
from core.perception.counter import ZoneCounter
from core.simulation.engine import TrafficSimulation
from utils.config_loader import load_zone_config
from utils.logger import get_logger

logger = get_logger(__name__)

@contextmanager
def video_capture(source: str):
    """Context manager for video stream (avoids leaks)."""
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {source}")
    try:
        yield cap
    finally:
        cap.release()
        logger.debug("Video resources released")

def process_frame(
    frame: np.ndarray,
    counter: ZoneCounter
) -> Dict[str, int]:
    """One-pass frame processing with direct ZoneCounter integration."""
    detections = counter.detect_vehicles(frame)
    tracked_objs = counter.tracker.update(
        detections,
        [frame.shape[0], frame.shape[1]],
        (frame.shape[0], frame.shape[1])
    )
    counter.update_counts(tracked_objs, frame.shape)
    return counter.zone_counts  # Returns zone_counts

def main(config_path: str = "configs/zones/intersection_a.json"):
    # Load configs once (O(1) startup)
    zone_config = load_zone_config(config_path)
    
    # Initialize components
    counter = ZoneCounter(config_path)
    sim = TrafficSimulation(zone_config)

    # Get absolute video path with validation
    video_path = (Path(__file__).parent.parent / "data" / "raw" / "rtvClip3.mp4")
    video_path = video_path.resolve()
    
    if not video_path.exists():
        available = [f.name for f in video_path.parent.glob("*.mp4")]
        raise FileNotFoundError(
            f"Video file not found at: {video_path}\n"
            f"Available videos: {available or 'None found'}"
        )
    
    logger.info(f"Processing video: {video_path}")

    with video_capture(str(video_path)) as cap:
        # Precompute video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = int(1000 / fps) if fps > 0 else 30

        while True:
            ret, frame = cap.read()
            if not ret:
                logger.info("End of video stream")
                break

            # Process frame
            zone_counts = process_frame(frame, counter)
            
            # Update simulation
            sim.update(zone_counts)
            
            # Render
            sim.render()
            
            # Exit on 'q' or ESC
            if cv2.waitKey(frame_delay) & 0xFF in (ord('q'), 27):
                logger.info("User requested exit")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise SystemExit(1)