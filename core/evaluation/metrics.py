#!/usr/bin/env python3
"""Traffic Performance Metrics Collection and Calculation"""

import time
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from pathlib import Path

@dataclass
class TrafficMetrics:
    """Comprehensive traffic light performance metrics"""
    
    # Core metrics
    vehicles_cleared_per_minute: float = 0.0
    average_wait_time_per_lane: Dict[str, float] = field(default_factory=dict)
    starvation_detection: Dict[str, int] = field(default_factory=dict)
    
    # Efficiency metrics
    throughput_efficiency: float = 0.0  # vehicles cleared / total vehicles
    lane_utilization: Dict[str, float] = field(default_factory=dict)
    signal_cycle_efficiency: float = 0.0
    
    # Quality of service metrics
    max_wait_time: float = 0.0
    queue_length_per_lane: Dict[str, int] = field(default_factory=dict)
    congestion_level: float = 0.0  # 0-1 scale
    
    # RL-specific metrics
    reward_history: List[float] = field(default_factory=list)
    action_distribution: Dict[int, int] = field(default_factory=dict)
    exploration_rate: float = 0.0
    
    # System performance
    fps: float = 0.0
    processing_time: float = 0.0
    memory_usage: float = 0.0
    
    def __post_init__(self):
        """Initialize tracking structures"""
        self.wait_times = defaultdict(list)
        self.queue_history = defaultdict(list)
        self.vehicle_counts = defaultdict(int)
        self.phase_durations = []
        self.last_update = time.time()
        
    def update_vehicle_cleared(self, lane: str, wait_time: float):
        """Update metrics when a vehicle clears the intersection"""
        self.vehicles_cleared_per_minute += 1
        self.wait_times[lane].append(wait_time)
        self.vehicle_counts[lane] += 1
        
        # Update max wait time
        if wait_time > self.max_wait_time:
            self.max_wait_time = wait_time
            
    def update_queue_length(self, lane: str, queue_length: int):
        """Update queue length for a lane"""
        self.queue_length_per_lane[lane] = queue_length
        self.queue_history[lane].append(queue_length)
        
        # Keep only recent history (last 100 entries)
        if len(self.queue_history[lane]) > 100:
            self.queue_history[lane] = self.queue_history[lane][-100:]
            
    def update_starvation(self, lane: str, starvation_time: float):
        """Detect and track lane starvation"""
        if starvation_time > 30.0:  # 30 seconds threshold
            self.starvation_detection[lane] = self.starvation_detection.get(lane, 0) + 1
            
    def update_phase_duration(self, duration: float):
        """Track signal phase durations"""
        self.phase_durations.append(duration)
        
        # Keep only recent history
        if len(self.phase_durations) > 50:
            self.phase_durations = self.phase_durations[-50:]
            
    def update_rl_metrics(self, reward: float, action: int, exploration_rate: float = None):
        """Update RL-specific metrics"""
        self.reward_history.append(reward)
        self.action_distribution[action] = self.action_distribution.get(action, 0) + 1
        
        if exploration_rate is not None:
            self.exploration_rate = exploration_rate
            
    def update_system_performance(self, fps: float, processing_time: float, memory_usage: float = None):
        """Update system performance metrics"""
        self.fps = fps
        self.processing_time = processing_time
        if memory_usage is not None:
            self.memory_usage = memory_usage
            
    def calculate_averages(self):
        """Calculate average metrics"""
        # Average wait time per lane
        for lane in self.wait_times:
            if self.wait_times[lane]:
                self.average_wait_time_per_lane[lane] = np.mean(self.wait_times[lane])
                
        # Lane utilization (based on vehicle counts)
        total_vehicles = sum(self.vehicle_counts.values())
        if total_vehicles > 0:
            for lane in self.vehicle_counts:
                self.lane_utilization[lane] = self.vehicle_counts[lane] / total_vehicles
                
        # Signal cycle efficiency (average phase duration)
        if self.phase_durations:
            self.signal_cycle_efficiency = np.mean(self.phase_durations)
            
        # Throughput efficiency
        total_vehicles_processed = sum(self.vehicle_counts.values())
        if total_vehicles_processed > 0:
            self.throughput_efficiency = self.vehicles_cleared_per_minute / total_vehicles_processed
            
        # Congestion level (based on average queue lengths)
        avg_queue_lengths = [np.mean(q) if q else 0 for q in self.queue_history.values()]
        if avg_queue_lengths:
            self.congestion_level = min(1.0, np.mean(avg_queue_lengths) / 10.0)  # Normalize to 0-1
            
    def get_summary(self) -> Dict:
        """Get a summary of all metrics"""
        self.calculate_averages()
        
        return {
            'core_metrics': {
                'vehicles_cleared_per_minute': self.vehicles_cleared_per_minute,
                'average_wait_time_per_lane': dict(self.average_wait_time_per_lane),
                'starvation_detection': dict(self.starvation_detection),
                'max_wait_time': self.max_wait_time
            },
            'efficiency_metrics': {
                'throughput_efficiency': self.throughput_efficiency,
                'lane_utilization': dict(self.lane_utilization),
                'signal_cycle_efficiency': self.signal_cycle_efficiency
            },
            'quality_metrics': {
                'queue_length_per_lane': dict(self.queue_length_per_lane),
                'congestion_level': self.congestion_level
            },
            'rl_metrics': {
                'avg_reward': np.mean(self.reward_history) if self.reward_history else 0.0,
                'action_distribution': dict(self.action_distribution),
                'exploration_rate': self.exploration_rate
            },
            'system_metrics': {
                'fps': self.fps,
                'processing_time': self.processing_time,
                'memory_usage': self.memory_usage
            }
        }
        
    def save_metrics(self, filepath: str):
        """Save metrics to JSON file"""
        summary = self.get_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
            
    def reset(self):
        """Reset all metrics"""
        self.__init__()
        
    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        self.calculate_averages()
        
        # Weighted scoring based on key metrics
        score = 0.0
        
        # Throughput (30% weight)
        throughput_score = min(100, self.vehicles_cleared_per_minute * 10)
        score += throughput_score * 0.3
        
        # Efficiency (25% weight)
        efficiency_score = self.throughput_efficiency * 100
        score += efficiency_score * 0.25
        
        # Wait time (20% weight)
        avg_wait_time = np.mean(list(self.average_wait_time_per_lane.values())) if self.average_wait_time_per_lane else 0
        wait_score = max(0, 100 - avg_wait_time * 2)  # Penalize high wait times
        score += wait_score * 0.2
        
        # Congestion (15% weight)
        congestion_score = (1 - self.congestion_level) * 100
        score += congestion_score * 0.15
        
        # System performance (10% weight)
        fps_score = min(100, self.fps * 2)  # Target 50+ FPS
        score += fps_score * 0.1
        
        return max(0, min(100, score)) 