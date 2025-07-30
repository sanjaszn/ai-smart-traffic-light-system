#!/usr/bin/env python3
"""Unit tests for RuleBasedScheduler"""

import pytest
import numpy as np
from core.control.rules.scheduler import RuleBasedScheduler

class TestRuleBasedScheduler:
    """Test RuleBasedScheduler functionality"""
    
    def test_initialization(self):
        """Test scheduler initialization"""
        scheduler = RuleBasedScheduler()
        
        assert scheduler.phase_duration == 10.0
        assert scheduler.last_phase == 0
        assert scheduler.phase_timer == 0.0
        
    def test_predict_basic(self, sample_traffic_state):
        """Test basic prediction functionality"""
        scheduler = RuleBasedScheduler()
        
        action = scheduler.predict(sample_traffic_state)
        
        # Check action format
        assert isinstance(action, np.ndarray)
        assert len(action) == 2
        assert action.dtype == np.float32
        
        # Check action values
        assert 0 <= action[0] <= 3  # Phase should be 0-3
        assert action[1] == 10.0  # Duration should be phase_duration
        
    def test_predict_max_count_rule(self):
        """Test max-count rule logic"""
        scheduler = RuleBasedScheduler()
        
        # State with clear maximum count
        state = {
            'zone_counts': [5, 3, 15, 2],  # Index 2 has highest count
            'current_phase': [0],
            'elapsed_time': [15.0]  # Over phase duration
        }
        
        action = scheduler.predict(state)
        
        # Should switch to direction with highest count (index 2)
        assert action[0] == 2
        assert action[1] == 10.0
        
    def test_predict_keep_current_phase(self):
        """Test keeping current phase when time hasn't elapsed"""
        scheduler = RuleBasedScheduler()
        
        # State with short elapsed time
        state = {
            'zone_counts': [5, 3, 15, 2],
            'current_phase': [1],
            'elapsed_time': [5.0]  # Under phase duration
        }
        
        action = scheduler.predict(state)
        
        # Should keep current phase
        assert action[0] == 1
        assert action[1] == 10.0
        
    def test_predict_cycle_when_same_max(self):
        """Test cycling when current phase has highest count"""
        scheduler = RuleBasedScheduler()
        
        # State where current phase has highest count
        state = {
            'zone_counts': [5, 3, 7, 2],  # Current phase (0) has 5, but index 2 has 7
            'current_phase': [2],
            'elapsed_time': [15.0]  # Over phase duration
        }
        
        action = scheduler.predict(state)
        
        # Should switch to direction with highest count (index 2)
        # But since current phase is 2, should cycle to next phase
        assert action[0] == 3  # Next phase after 2
        assert action[1] == 10.0
        
    def test_predict_edge_cases(self):
        """Test edge cases"""
        scheduler = RuleBasedScheduler()
        
        # Empty state
        empty_state = {
            'zone_counts': [0, 0, 0, 0],
            'current_phase': [0],
            'elapsed_time': [15.0]
        }
        
        action = scheduler.predict(empty_state)
        assert 0 <= action[0] <= 3
        assert action[1] == 10.0
        
        # Single non-zero count
        single_state = {
            'zone_counts': [0, 0, 10, 0],
            'current_phase': [0],
            'elapsed_time': [15.0]
        }
        
        action = scheduler.predict(single_state)
        assert action[0] == 2  # Should choose index 2
        
    def test_reset(self):
        """Test scheduler reset"""
        scheduler = RuleBasedScheduler()
        
        # Change some values
        scheduler.last_phase = 2
        scheduler.phase_timer = 5.0
        
        # Reset
        scheduler.reset()
        
        # Check reset values
        assert scheduler.last_phase == 0
        assert scheduler.phase_timer == 0.0
        
    def test_phase_duration_configuration(self):
        """Test different phase duration configurations"""
        # Test with custom phase duration
        scheduler = RuleBasedScheduler()
        scheduler.phase_duration = 15.0
        
        state = {
            'zone_counts': [5, 3, 7, 2],
            'current_phase': [0],
            'elapsed_time': [20.0]  # Over new phase duration
        }
        
        action = scheduler.predict(state)
        assert action[1] == 15.0  # Should use custom duration
        
    def test_multiple_predictions(self):
        """Test multiple consecutive predictions"""
        scheduler = RuleBasedScheduler()
        
        # First prediction
        state1 = {
            'zone_counts': [5, 3, 7, 2],
            'current_phase': [0],
            'elapsed_time': [15.0]
        }
        
        action1 = scheduler.predict(state1)
        assert action1[0] == 2  # Should choose index 2 (highest count)
        
        # Second prediction with same state
        action2 = scheduler.predict(state1)
        assert action2[0] == 2  # Should still choose index 2
        
        # Third prediction with different state
        state2 = {
            'zone_counts': [10, 3, 7, 2],  # Now index 0 has highest
            'current_phase': [2],
            'elapsed_time': [15.0]
        }
        
        action3 = scheduler.predict(state2)
        assert action3[0] == 0  # Should choose index 0 