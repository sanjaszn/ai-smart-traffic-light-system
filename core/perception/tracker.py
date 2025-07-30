#!/usr/bin/env python3
"""ByteTrack Multi-Object Tracker Module"""
import sys
import os
import numpy as np
from argparse import Namespace
from typing import List, Tuple, Optional

# Add ByteTrack to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ByteTrack')))
from yolox.tracker.byte_tracker import BYTETracker

class VehicleTracker:
    """ByteTrack-based vehicle tracking with ID smoothing"""
    
    def __init__(self, track_thresh: float = 0.5, match_thresh: float = 0.8, 
                 track_buffer: int = 30, aspect_ratio_thresh: float = 1.6,
                 min_box_area: int = 10):
        """
        Initialize ByteTrack tracker
        
        Args:
            track_thresh: Detection confidence threshold
            match_thresh: Matching threshold for tracking
            track_buffer: Number of frames to keep track history
            aspect_ratio_thresh: Maximum aspect ratio for valid tracks
            min_box_area: Minimum bounding box area
        """
        args = Namespace(
            track_thresh=track_thresh,
            match_thresh=match_thresh,
            track_buffer=track_buffer,
            aspect_ratio_thresh=aspect_ratio_thresh,
            min_box_area=min_box_area,
            mot20=False
        )
        self.tracker = BYTETracker(args)
        
        # Track statistics
        self.track_count = 0
        self.lost_tracks = 0
        self.active_tracks = 0
    
    def update(self, detections: np.ndarray, frame_shape: Tuple[int, int]) -> List:
        """
        Update tracker with new detections
        
        Args:
            detections: Array of [x1, y1, x2, y2, confidence] detections
            frame_shape: (height, width) of input frame
            
        Returns:
            tracked_objects: List of tracked objects with IDs
        """
        try:
            # Update tracker
            tracked_objs = self.tracker.update(
                detections, 
                [frame_shape[0], frame_shape[1]], 
                (frame_shape[0], frame_shape[1])
            )
            
            # Update statistics
            self.active_tracks = len(tracked_objs)
            self.track_count = max(self.track_count, 
                                 max([obj.track_id for obj in tracked_objs]) if tracked_objs else 0)
            
            return tracked_objs
            
        except Exception as e:
            print(f"Tracking error: {e}")
            return []
    
    def get_track_stats(self) -> dict:
        """
        Get tracking statistics
        
        Returns:
            stats: Dictionary with tracking statistics
        """
        return {
            'total_tracks': self.track_count,
            'active_tracks': self.active_tracks,
            'lost_tracks': self.lost_tracks,
            'track_quality': self.active_tracks / max(self.track_count, 1)
        }
    
    def filter_tracks_by_zone(self, tracked_objs: List, zone_polygon: np.ndarray) -> List:
        """
        Filter tracks that are within a specific zone
        
        Args:
            tracked_objs: List of tracked objects
            zone_polygon: Polygon defining the zone
            
        Returns:
            filtered_tracks: Tracks within the zone
        """
        import cv2
        
        filtered_tracks = []
        for track in tracked_objs:
            x1, y1, w, h = map(int, track.tlwh)
            x2, y2 = x1 + w, y1 + h
            
            # Check if track center is in zone
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
            if cv2.pointPolygonTest(zone_polygon, (center_x, center_y), False) >= 0:
                filtered_tracks.append(track)
        
        return filtered_tracks
    
    def get_track_trajectories(self, tracked_objs: List, max_history: int = 10) -> dict:
        """
        Get trajectory history for tracked objects
        
        Args:
            tracked_objs: List of tracked objects
            max_history: Maximum number of historical points to keep
            
        Returns:
            trajectories: Dictionary mapping track_id to trajectory points
        """
        trajectories = {}
        
        for track in tracked_objs:
            track_id = track.track_id
            x1, y1, w, h = map(int, track.tlwh)
            center_x, center_y = (x1 + w) // 2, (y1 + h) // 2
            
            if track_id not in trajectories:
                trajectories[track_id] = []
            
            trajectories[track_id].append((center_x, center_y))
            
            # Keep only recent history
            if len(trajectories[track_id]) > max_history:
                trajectories[track_id] = trajectories[track_id][-max_history:]
        
        return trajectories 