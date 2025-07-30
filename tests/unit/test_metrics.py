#!/usr/bin/env python3
"""Unit tests for TrafficMetrics"""

import pytest
import numpy as np
from core.evaluation import TrafficMetrics

class TestTrafficMetrics:
    """Test TrafficMetrics functionality"""
    
    def test_initialization(self):
        """Test TrafficMetrics initialization"""
        metrics = TrafficMetrics()
        
        assert metrics.vehicles_cleared_per_minute == 0.0
        assert metrics.average_wait_time_per_lane == {}
        assert metrics.starvation_detection == {}
        assert metrics.throughput_efficiency == 0.0
        assert metrics.max_wait_time == 0.0
        assert metrics.reward_history == []
        assert metrics.action_distribution == {}
        
    def test_update_vehicle_cleared(self):
        """Test vehicle cleared metrics update"""
        metrics = TrafficMetrics()
        
        # Update vehicle cleared
        metrics.update_vehicle_cleared("north", 15.5)
        metrics.update_vehicle_cleared("south", 20.0)
        
        assert metrics.vehicles_cleared_per_minute == 2.0
        assert metrics.max_wait_time == 20.0
        assert "north" in metrics.wait_times
        assert "south" in metrics.wait_times
        assert len(metrics.wait_times["north"]) == 1
        assert len(metrics.wait_times["south"]) == 1
        
    def test_update_queue_length(self):
        """Test queue length metrics update"""
        metrics = TrafficMetrics()
        
        metrics.update_queue_length("north", 5)
        metrics.update_queue_length("south", 3)
        
        assert metrics.queue_length_per_lane["north"] == 5
        assert metrics.queue_length_per_lane["south"] == 3
        assert len(metrics.queue_history["north"]) == 1
        assert len(metrics.queue_history["south"]) == 1
        
    def test_update_starvation(self):
        """Test starvation detection"""
        metrics = TrafficMetrics()
        
        # Test no starvation
        metrics.update_starvation("north", 15.0)
        assert "north" not in metrics.starvation_detection
        
        # Test starvation (over 30 seconds)
        metrics.update_starvation("south", 35.0)
        assert metrics.starvation_detection["south"] == 1
        
        # Test multiple starvation events
        metrics.update_starvation("south", 40.0)
        assert metrics.starvation_detection["south"] == 2
        
    def test_update_phase_duration(self):
        """Test phase duration tracking"""
        metrics = TrafficMetrics()
        
        metrics.update_phase_duration(20.0)
        metrics.update_phase_duration(25.0)
        metrics.update_phase_duration(30.0)
        
        assert len(metrics.phase_durations) == 3
        assert metrics.phase_durations == [20.0, 25.0, 30.0]
        
    def test_update_rl_metrics(self):
        """Test RL metrics update"""
        metrics = TrafficMetrics()
        
        metrics.update_rl_metrics(0.8, 1)
        metrics.update_rl_metrics(0.6, 2)
        metrics.update_rl_metrics(0.9, 1)
        
        assert len(metrics.reward_history) == 3
        assert metrics.reward_history == [0.8, 0.6, 0.9]
        assert metrics.action_distribution == {1: 2, 2: 1}
        
    def test_update_system_performance(self):
        """Test system performance metrics"""
        metrics = TrafficMetrics()
        
        metrics.update_system_performance(60.0, 0.016, 128.5)
        
        assert metrics.fps == 60.0
        assert metrics.processing_time == 0.016
        assert metrics.memory_usage == 128.5
        
    def test_calculate_averages(self):
        """Test average calculations"""
        metrics = TrafficMetrics()
        
        # Add some data
        metrics.update_vehicle_cleared("north", 10.0)
        metrics.update_vehicle_cleared("north", 20.0)
        metrics.update_vehicle_cleared("south", 15.0)
        
        metrics.update_queue_length("north", 5)
        metrics.update_queue_length("south", 3)
        
        metrics.update_phase_duration(20.0)
        metrics.update_phase_duration(30.0)
        
        # Calculate averages
        metrics.calculate_averages()
        
        # Check results
        assert metrics.average_wait_time_per_lane["north"] == 15.0
        assert metrics.average_wait_time_per_lane["south"] == 15.0
        assert metrics.signal_cycle_efficiency == 25.0
        assert metrics.lane_utilization["north"] == 2/3  # 2 out of 3 vehicles
        assert metrics.lane_utilization["south"] == 1/3  # 1 out of 3 vehicles
        
    def test_get_summary(self):
        """Test summary generation"""
        metrics = TrafficMetrics()
        
        # Add comprehensive data
        metrics.update_vehicle_cleared("north", 15.0)
        metrics.update_queue_length("north", 5)
        metrics.update_phase_duration(25.0)
        metrics.update_rl_metrics(0.8, 1)
        metrics.update_system_performance(60.0, 0.016)
        
        summary = metrics.get_summary()
        
        # Check structure
        assert 'core_metrics' in summary
        assert 'efficiency_metrics' in summary
        assert 'quality_metrics' in summary
        assert 'rl_metrics' in summary
        assert 'system_metrics' in summary
        
        # Check values
        assert summary['core_metrics']['vehicles_cleared_per_minute'] == 1.0
        assert summary['core_metrics']['max_wait_time'] == 15.0
        assert summary['efficiency_metrics']['signal_cycle_efficiency'] == 25.0
        assert summary['rl_metrics']['avg_reward'] == 0.8
        assert summary['system_metrics']['fps'] == 60.0
        
    def test_get_performance_score(self):
        """Test performance score calculation"""
        metrics = TrafficMetrics()
        
        # Add good performance data
        metrics.update_vehicle_cleared("north", 10.0)  # Low wait time
        metrics.update_queue_length("north", 2)  # Low queue
        metrics.update_system_performance(60.0, 0.016)  # Good FPS
        
        score = metrics.get_performance_score()
        
        # Score should be reasonable (not 0)
        assert score > 0
        assert score <= 100
        
    def test_reset(self):
        """Test metrics reset"""
        metrics = TrafficMetrics()
        
        # Add some data
        metrics.update_vehicle_cleared("north", 15.0)
        metrics.update_queue_length("north", 5)
        metrics.update_rl_metrics(0.8, 1)
        
        # Reset
        metrics.reset()
        
        # Check everything is reset
        assert metrics.vehicles_cleared_per_minute == 0.0
        assert metrics.average_wait_time_per_lane == {}
        assert metrics.reward_history == []
        assert metrics.action_distribution == {}
        
    def test_save_metrics(self, temp_data_file):
        """Test metrics saving to file"""
        metrics = TrafficMetrics()
        
        # Add some data
        metrics.update_vehicle_cleared("north", 15.0)
        metrics.update_queue_length("north", 5)
        
        # Save to file
        metrics.save_metrics(temp_data_file)
        
        # Check file was created and contains data
        import json
        with open(temp_data_file, 'r') as f:
            saved_data = json.load(f)
            
        assert 'core_metrics' in saved_data
        assert saved_data['core_metrics']['vehicles_cleared_per_minute'] == 1.0 