#!/usr/bin/env python3
"""Rule-Based Traffic Light Scheduler"""
import numpy as np
from typing import Dict, Any

class RuleBasedScheduler:
    """Simple rule-based traffic light controller for benchmarking"""
    
    def __init__(self):
        self.phase_duration = 10.0  # Fixed duration per phase
        self.last_phase = 0
        self.phase_timer = 0.0
        
    def predict(self, observation: Dict[str, Any]) -> np.ndarray:
        """
        Rule-based decision making
        
        Args:
            observation: Dict with 'zone_counts', 'current_phase', 'elapsed_time'
            
        Returns:
            action: [direction, duration] where direction is 0-3 (N,E,S,W)
        """
        zone_counts = observation['zone_counts']
        current_phase = observation['current_phase'][0]
        elapsed_time = observation['elapsed_time'][0]
        
        # Simple max-count rule
        if elapsed_time >= self.phase_duration:
            # Switch to direction with highest count
            next_phase = np.argmax(zone_counts)
            if next_phase == current_phase:
                # If current phase has highest count, cycle to next
                next_phase = (current_phase + 1) % 4
        else:
            # Keep current phase
            next_phase = current_phase
            
        return np.array([next_phase, self.phase_duration], dtype=np.float32)
    
    def reset(self):
        """Reset scheduler state"""
        self.last_phase = 0
        self.phase_timer = 0.0 