#!/usr/bin/env python3
"""Integration tests for evaluation pipeline"""

import pytest
import time
import json
from pathlib import Path
from core.evaluation import TrafficMetrics, BenchmarkRunner, MetricsVisualizer
from core.evaluation.benchmark import BenchmarkConfig
from core.control.rules.scheduler import RuleBasedScheduler
from core.utils.mock_zone_generator import MockZoneGenerator

class TestEvaluationPipeline:
    """Test the complete evaluation pipeline"""
    
    def test_metrics_to_benchmark_integration(self, temp_output_dir):
        """Test integration between metrics and benchmark runner"""
        # Setup
        config = BenchmarkConfig(
            duration_minutes=1,  # Short for testing
            traffic_scenarios=['low'],
            controllers=['rule-based'],
            output_dir=temp_output_dir
        )
        
        benchmark_runner = BenchmarkRunner(config)
        metrics = TrafficMetrics()
        
        # Test that metrics can be used with benchmark runner
        assert benchmark_runner.metrics_collector is not None
        assert isinstance(benchmark_runner.metrics_collector, TrafficMetrics)
        
    def test_scheduler_to_metrics_integration(self, sample_traffic_state):
        """Test integration between scheduler and metrics"""
        scheduler = RuleBasedScheduler()
        metrics = TrafficMetrics()
        
        # Get action from scheduler
        action = scheduler.predict(sample_traffic_state)
        
        # Update metrics with action
        metrics.update_rl_metrics(0.8, int(action[0]))
        metrics.update_phase_duration(action[1])
        
        # Check integration worked
        assert len(metrics.reward_history) == 1
        assert metrics.reward_history[0] == 0.8
        assert len(metrics.phase_durations) == 1
        assert metrics.phase_durations[0] == action[1]
        
    def test_mock_generator_to_metrics_integration(self, temp_data_file):
        """Test integration between mock generator and metrics"""
        generator = MockZoneGenerator(temp_data_file, refresh_rate=1.0)
        metrics = TrafficMetrics()
        
        # Generate counts
        counts = generator.generate_counts()
        
        # Update metrics with counts
        for i, (zone, count) in enumerate(counts.items()):
            lane = f"lane_{i}"
            metrics.update_queue_length(lane, count)
            
        # Check integration worked
        assert len(metrics.queue_length_per_lane) == 4
        assert all(lane in metrics.queue_length_per_lane for lane in [f"lane_{i}" for i in range(4)])
        
    def test_visualizer_to_metrics_integration(self, temp_output_dir, sample_metrics_data):
        """Test integration between visualizer and metrics"""
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        # Create metrics summary
        metrics = TrafficMetrics()
        metrics.update_vehicle_cleared("north", 15.0)
        metrics.update_queue_length("north", 5)
        
        summary = metrics.get_summary()
        
        # Use visualizer with metrics data
        benchmark_results = [
            {
                'scenario': 'test',
                'controller': 'test',
                'performance_score': 75.0,
                'metrics': summary
            }
        ]
        
        # Generate plot
        plot_path = visualizer.plot_performance_comparison(benchmark_results)
        
        # Check integration worked
        assert Path(plot_path).exists()
        
    def test_complete_evaluation_flow(self, temp_output_dir, temp_data_file):
        """Test complete evaluation flow from data generation to visualization"""
        # 1. Generate mock data
        generator = MockZoneGenerator(temp_data_file, refresh_rate=1.0)
        counts = generator.generate_counts()
        generator.output_path.write_text(json.dumps(counts, indent=2))
        
        # 2. Create traffic state
        state = {
            'zone_counts': list(counts.values()),
            'current_phase': [0],
            'elapsed_time': [10.0]
        }
        
        # 3. Get controller action
        scheduler = RuleBasedScheduler()
        action = scheduler.predict(state)
        
        # 4. Collect metrics
        metrics = TrafficMetrics()
        metrics.update_rl_metrics(0.8, int(action[0]))
        metrics.update_phase_duration(action[1])
        
        for i, count in enumerate(counts.values()):
            lane = f"lane_{i}"
            metrics.update_queue_length(lane, count)
            
        # 5. Generate visualization
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        summary = metrics.get_summary()
        
        benchmark_results = [
            {
                'scenario': 'integration_test',
                'controller': 'rule-based',
                'performance_score': metrics.get_performance_score(),
                'metrics': summary
            }
        ]
        
        plot_path = visualizer.plot_performance_comparison(benchmark_results)
        
        # 6. Verify complete flow worked
        assert Path(temp_data_file).exists()
        assert len(metrics.reward_history) == 1
        assert len(metrics.phase_durations) == 1
        assert Path(plot_path).exists()
        
    def test_benchmark_configuration_integration(self, temp_output_dir):
        """Test benchmark configuration integration"""
        config = BenchmarkConfig(
            duration_minutes=1,
            traffic_scenarios=['low', 'medium'],
            controllers=['rule-based', 'rl-agent'],
            output_dir=temp_output_dir
        )
        
        benchmark_runner = BenchmarkRunner(config)
        
        # Test that configuration is properly integrated
        assert benchmark_runner.config == config
        assert benchmark_runner.output_dir == Path(temp_output_dir)
        assert len(benchmark_runner.config.traffic_scenarios) == 2
        assert len(benchmark_runner.config.controllers) == 2
        
    def test_error_handling_integration(self, temp_output_dir):
        """Test error handling across components"""
        # Test with invalid data
        metrics = TrafficMetrics()
        
        # Should handle invalid inputs gracefully
        try:
            metrics.update_vehicle_cleared("north", "invalid")
            metrics.update_queue_length("north", "invalid")
        except Exception as e:
            pytest.fail(f"Metrics should handle invalid inputs gracefully: {e}")
            
        # Test with missing data
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        
        try:
            # Should handle empty results
            plot_path = visualizer.plot_performance_comparison([])
            assert Path(plot_path).exists()
        except Exception as e:
            pytest.fail(f"Visualizer should handle empty data gracefully: {e}")
            
    def test_performance_integration(self, temp_output_dir):
        """Test performance of integrated components"""
        start_time = time.time()
        
        # Run complete evaluation flow
        config = BenchmarkConfig(
            duration_minutes=1,
            traffic_scenarios=['low'],
            controllers=['rule-based'],
            output_dir=temp_output_dir
        )
        
        benchmark_runner = BenchmarkRunner(config)
        metrics = TrafficMetrics()
        
        # Simulate some processing
        for i in range(10):
            metrics.update_vehicle_cleared("north", 10 + i)
            metrics.update_queue_length("north", i)
            metrics.update_rl_metrics(0.5 + i * 0.1, i % 4)
            
        # Generate visualization
        visualizer = MetricsVisualizer(output_dir=temp_output_dir)
        summary = metrics.get_summary()
        
        benchmark_results = [
            {
                'scenario': 'performance_test',
                'controller': 'rule-based',
                'performance_score': metrics.get_performance_score(),
                'metrics': summary
            }
        ]
        
        plot_path = visualizer.plot_performance_comparison(benchmark_results)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        assert processing_time < 10.0  # Should complete within 10 seconds
        assert Path(plot_path).exists()
        
    def test_data_persistence_integration(self, temp_output_dir, temp_data_file):
        """Test data persistence across components"""
        # Generate data
        generator = MockZoneGenerator(temp_data_file, refresh_rate=1.0)
        counts = generator.generate_counts()
        generator.output_path.write_text(json.dumps(counts, indent=2))
        
        # Process data
        metrics = TrafficMetrics()
        for i, count in enumerate(counts.values()):
            lane = f"lane_{i}"
            metrics.update_queue_length(lane, count)
            
        # Save metrics
        metrics_file = Path(temp_output_dir) / "test_metrics.json"
        metrics.save_metrics(str(metrics_file))
        
        # Verify persistence
        assert Path(temp_data_file).exists()
        assert metrics_file.exists()
        
        # Load and verify data
        with open(metrics_file, 'r') as f:
            saved_metrics = json.load(f)
            
        assert 'core_metrics' in saved_metrics
        assert 'quality_metrics' in saved_metrics 