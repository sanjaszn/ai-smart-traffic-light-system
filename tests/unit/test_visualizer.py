#!/usr/bin/env python3
"""Unit tests for MetricsVisualizer"""

import pytest
import os
from pathlib import Path
from core.evaluation import MetricsVisualizer

class TestMetricsVisualizer:
    """Test MetricsVisualizer functionality"""
    
    def test_initialization(self, temp_output_dir):
        """Test visualizer initialization"""
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        assert visualizer.output_dir == Path(temp_output_dir)
        assert visualizer.output_dir.exists()
        
    def test_plot_performance_comparison(self, temp_output_dir, sample_metrics_data):
        """Test performance comparison plot generation"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Create dummy benchmark results
        benchmark_results = [
            {
                'scenario': 'low',
                'controller': 'rule-based',
                'performance_score': 75.5,
                'metrics': sample_metrics_data
            },
            {
                'scenario': 'low',
                'controller': 'rl-agent',
                'performance_score': 82.3,
                'metrics': sample_metrics_data
            }
        ]
        
        # Generate plot
        plot_path = visualizer.plot_performance_comparison(benchmark_results)
        
        # Check plot was created
        assert Path(plot_path).exists()
        assert plot_path.endswith('.png')
        
    def test_plot_lane_analysis(self, temp_output_dir, sample_metrics_data):
        """Test lane analysis plot generation"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Generate plot
        plot_path = visualizer.plot_lane_analysis(sample_metrics_data)
        
        # Check plot was created
        assert Path(plot_path).exists()
        assert plot_path.endswith('.png')
        
    def test_plot_rl_analysis(self, temp_output_dir, sample_metrics_data):
        """Test RL analysis plot generation"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Generate plot
        plot_path = visualizer.plot_rl_analysis(sample_metrics_data)
        
        # Check plot was created
        assert Path(plot_path).exists()
        assert plot_path.endswith('.png')
        
    def test_create_dashboard(self, temp_output_dir, sample_metrics_data):
        """Test dashboard creation"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Create dummy benchmark results
        benchmark_results = [
            {
                'scenario': 'low',
                'controller': 'rule-based',
                'performance_score': 75.5,
                'metrics': sample_metrics_data
            }
        ]
        
        # Generate dashboard
        dashboard_path = visualizer.create_dashboard(benchmark_results)
        
        # Check dashboard was created
        assert Path(dashboard_path).exists()
        assert dashboard_path.endswith('.html')
        
        # Check HTML content
        with open(dashboard_path, 'r') as f:
            content = f.read()
            assert 'AI Traffic Light System Dashboard' in content
            assert 'Performance Evaluation' in content
            
    def test_calculate_performance_score_from_metrics(self, sample_metrics_data):
        """Test performance score calculation from metrics"""
        visualizer = MetricsVisualizer()
        
        score = visualizer._calculate_performance_score_from_metrics(sample_metrics_data)
        
        # Score should be reasonable
        assert score > 0
        assert score <= 100
        
    def test_plot_with_empty_data(self, temp_output_dir):
        """Test plotting with empty data"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Test with empty benchmark results
        empty_results = []
        
        # Should handle empty data gracefully
        plot_path = visualizer.plot_performance_comparison(empty_results)
        
        # Should still create a plot (even if empty)
        assert Path(plot_path).exists()
        
    def test_plot_with_missing_metrics(self, temp_output_dir):
        """Test plotting with missing metrics data"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Create results with missing metrics
        incomplete_results = [
            {
                'scenario': 'low',
                'controller': 'rule-based',
                'performance_score': 75.5,
                'metrics': {
                    'core_metrics': {
                        'vehicles_cleared_per_minute': 25.0,
                        'average_wait_time_per_lane': {'north': 10.0},  # Add required field
                        'starvation_detection': {'north': 0},
                        'max_wait_time': 20.0
                    }
                    # Missing other metrics
                }
            }
        ]
        
        # Should handle missing data gracefully
        plot_path = visualizer.plot_performance_comparison(incomplete_results)
        assert Path(plot_path).exists()
        
    def test_output_directory_creation(self):
        """Test automatic output directory creation"""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        test_output_dir = os.path.join(temp_dir, "test_plots")
        
        try:
            # Should create directory if it doesn't exist
            visualizer = MetricsVisualizer(output_dir=test_output_dir)
            
            assert Path(test_output_dir).exists()
            assert visualizer.output_dir == Path(test_output_dir)
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
            
    def test_multiple_plot_generation(self, temp_output_dir, sample_metrics_data):
        """Test generating multiple plots"""
        # Set matplotlib to use non-interactive backend for testing
        import matplotlib
        matplotlib.use('Agg')
        
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        benchmark_results = [
            {
                'scenario': 'low',
                'controller': 'rule-based',
                'performance_score': 75.5,
                'metrics': sample_metrics_data
            }
        ]
        
        # Generate multiple plots
        plot1 = visualizer.plot_performance_comparison(benchmark_results)
        plot2 = visualizer.plot_lane_analysis(sample_metrics_data)
        plot3 = visualizer.plot_rl_analysis(sample_metrics_data)
        
        # All plots should be created
        assert Path(plot1).exists()
        assert Path(plot2).exists()
        assert Path(plot3).exists()
        
        # Should be different files
        assert plot1 != plot2
        assert plot2 != plot3
        assert plot1 != plot3 