#!/usr/bin/env python3
"""Pytest configuration and shared fixtures"""

import pytest
import sys
import os
import tempfile
import json
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        test_data = {
            "Zone A": 5,
            "Zone B": 3,
            "Zone C": 7,
            "Zone D": 2
        }
        json.dump(test_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture
def sample_traffic_state():
    """Sample traffic state for testing"""
    return {
        'zone_counts': [5, 3, 7, 2],
        'current_phase': [0],
        'elapsed_time': [15.0]
    }

@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return {
        'core_metrics': {
            'vehicles_cleared_per_minute': 25.0,
            'average_wait_time_per_lane': {'north': 12.5, 'south': 15.2},
            'starvation_detection': {'north': 0, 'south': 1},
            'max_wait_time': 45.0
        },
        'efficiency_metrics': {
            'throughput_efficiency': 0.85,
            'lane_utilization': {'north': 0.4, 'south': 0.6},
            'signal_cycle_efficiency': 25.0
        },
        'quality_metrics': {
            'queue_length_per_lane': {'north': 3, 'south': 5},
            'congestion_level': 0.3
        },
        'rl_metrics': {
            'avg_reward': 0.75,
            'action_distribution': {0: 10, 1: 15, 2: 8, 3: 12},
            'exploration_rate': 0.1
        },
        'system_metrics': {
            'fps': 60.0,
            'processing_time': 0.016,
            'memory_usage': 128.5
        }
    }

@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix="test_output_")
    yield temp_dir
    
    # Cleanup
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

@pytest.fixture
def mock_zone_counts():
    """Mock zone counts for testing"""
    return {
        "Zone A": 8,
        "Zone B": 12,
        "Zone C": 5,
        "Zone D": 15
    } 