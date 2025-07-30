#!/usr/bin/env python3
"""Video Processing Tool for AI Traffic Light System"""
import sys
import os
import cv2
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add ByteTrack to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ByteTrack')))

from core.perception.counter import ZoneCounter
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_video(video_path: str, output_path: str = None, display: bool = False):
    """Process video and generate zone counts"""
    
    if output_path is None:
        output_path = "data/processed/zone_counts.json"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting video processing: {video_path}")
        
        # Initialize zone counter
        counter = ZoneCounter()
        
        # Process video
        zone_counts = counter.run(
            video_path=video_path,
            display=display,
            output_path=output_path
        )
        
        logger.info(f"Video processing completed. Zone counts: {zone_counts}")
        return zone_counts
        
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        raise

def main():
    """Main function for video processing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process video for traffic light system")
    parser.add_argument("video_path", help="Path to video file")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--display", "-d", action="store_true", help="Display video processing")
    
    args = parser.parse_args()
    
    try:
        process_video(args.video_path, args.output, args.display)
    except Exception as e:
        logger.error(f"Failed to process video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 