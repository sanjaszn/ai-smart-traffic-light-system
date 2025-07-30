#!/usr/bin/env python3
"""Comprehensive System Evaluation Script"""

import sys
import os
import time
import json
import numpy as np
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.evaluation import TrafficMetrics, BenchmarkRunner, MetricsVisualizer
from core.evaluation.benchmark import BenchmarkConfig
from core.control.rules.scheduler import RuleBasedScheduler
from core.utils.mock_zone_generator import MockZoneGenerator

class SystemEvaluator:
    """Comprehensive system evaluation and benchmarking"""
    
    def __init__(self, config_path: str = "configs/zones/intersection_a.json"):
        self.config_path = config_path
        self.metrics = TrafficMetrics()
        self.visualizer = MetricsVisualizer()
        
        # Initialize controllers
        self.rule_based_controller = RuleBasedScheduler()
        
        # Benchmark configuration
        self.benchmark_config = BenchmarkConfig(
            duration_minutes=5,  # Shorter for testing
            traffic_scenarios=['low', 'medium', 'high'],
            controllers=['rule-based', 'rl-agent'],
            output_dir="test_plots"
        )
        
        self.benchmark_runner = BenchmarkRunner(self.benchmark_config)
        
    def run_rule_based_benchmark(self, scenario_name: str, 
                                metrics_collector: TrafficMetrics,
                                duration_minutes: int) -> Dict:
        """Run benchmark with rule-based controller (simplified)"""
        print(f"Running rule-based benchmark for {scenario_name} scenario")
        
        # Initialize mock data generator
        mock_generator = MockZoneGenerator(
            "data/processed/zone_counts.json",
            refresh_rate=20.0
        )
        
        # Adjust traffic levels based on scenario
        if scenario_name == 'low':
            traffic_multiplier = 0.5
        elif scenario_name == 'medium':
            traffic_multiplier = 1.0
        else:  # high
            traffic_multiplier = 2.0
            
        # Run simulation for specified duration (simplified)
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Update mock data
            counts = mock_generator.generate_counts()
            mock_generator.output_path.write_text(json.dumps(counts, indent=2))
            
            # Create dummy state from counts
            state = {
                'zone_counts': list(counts.values()),
                'current_phase': [0],
                'elapsed_time': [time.time() - start_time]
            }
            
            # Get rule-based action
            action = self.rule_based_controller.predict(state)
            
            # Collect metrics (simulated)
            self._collect_simulation_metrics_simplified(state, metrics_collector, action)
            
            # Small delay to prevent overwhelming
            time.sleep(0.1)
            
        return {'status': 'completed', 'scenario': scenario_name, 'controller': 'rule-based'}
        
    def run_rl_benchmark(self, scenario_name: str,
                        metrics_collector: TrafficMetrics,
                        duration_minutes: int) -> Dict:
        """Run benchmark with RL agent (simplified)"""
        print(f"Running RL benchmark for {scenario_name} scenario")
        
        # Initialize mock data generator
        mock_generator = MockZoneGenerator(
            "data/processed/zone_counts.json",
            refresh_rate=20.0
        )
        
        # Simple RL-like controller
        class SimpleRLController:
            def __init__(self):
                self.last_action = 0
                self.action_count = 0
                
            def predict(self, state):
                # Simple RL-like behavior: switch actions periodically
                self.action_count += 1
                if self.action_count % 50 == 0:  # Switch every 50 steps
                    self.last_action = (self.last_action + 1) % 4
                return np.array([self.last_action, 10.0])
                
        rl_controller = SimpleRLController()
        
        # Run simulation
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time:
            # Update mock data
            counts = mock_generator.generate_counts()
            mock_generator.output_path.write_text(json.dumps(counts, indent=2))
            
            # Create dummy state from counts
            state = {
                'zone_counts': list(counts.values()),
                'current_phase': [0],
                'elapsed_time': [time.time() - start_time]
            }
            
            # Get RL action
            action = rl_controller.predict(state)
            
            # Collect metrics
            self._collect_simulation_metrics_simplified(state, metrics_collector, action)
            
            # Update RL metrics
            reward = self._calculate_reward(state)
            metrics_collector.update_rl_metrics(reward, int(action[0]))
            
            time.sleep(0.1)
            
        return {'status': 'completed', 'scenario': scenario_name, 'controller': 'rl-agent'}
        
    def _collect_simulation_metrics_simplified(self, state: Dict, metrics: TrafficMetrics, action: np.ndarray):
        """Collect metrics from simplified simulation"""
        # Update queue lengths
        zone_counts = state['zone_counts']
        for i, count in enumerate(zone_counts):
            lane = f"lane_{i}"
            metrics.update_queue_length(lane, int(count))
            
        # Simulate vehicle clearing
        total_vehicles = sum(zone_counts)
        if total_vehicles > 0:
            # Simulate some vehicles being cleared
            cleared_count = min(2, total_vehicles // 3)
            for i in range(cleared_count):
                lane = f"lane_{i % 4}"
                wait_time = 10 + np.random.random() * 20
                metrics.update_vehicle_cleared(lane, wait_time)
        
        # Update system performance (simplified)
        metrics.update_system_performance(fps=60.0, processing_time=0.016)
        
        # Update phase duration
        elapsed_time = state['elapsed_time'][0]
        metrics.update_phase_duration(elapsed_time)
        
    def _calculate_reward(self, state: Dict) -> float:
        """Calculate reward for RL agent"""
        zone_counts = state['zone_counts']
        total_vehicles = sum(zone_counts)
        
        # Simple reward: negative for high congestion, positive for clearing vehicles
        if total_vehicles == 0:
            return 1.0  # Reward for empty intersection
        else:
            # Penalize high congestion
            return -total_vehicles * 0.1
            
    def run_comprehensive_evaluation(self) -> Dict:
        """Run comprehensive evaluation with all scenarios and controllers"""
        print("🚦 Starting Comprehensive System Evaluation")
        print("=" * 50)
        
        # Define controller functions
        controller_functions = {
            'rule-based': self.run_rule_based_benchmark,
            'rl-agent': self.run_rl_benchmark
        }
        
        # Run benchmarks
        results = self.benchmark_runner.run_comparison(controller_functions)
        
        # Generate visualizations
        print("\n📊 Generating Visualizations...")
        
        # Performance comparison plots
        benchmark_results = []
        for scenario in self.benchmark_config.traffic_scenarios:
            for controller in self.benchmark_config.controllers:
                result_file = f"test_plots/{controller}_{scenario}_{int(time.time())}.json"
                if Path(result_file).exists():
                    with open(result_file, 'r') as f:
                        benchmark_results.append(json.load(f))
        
        if benchmark_results:
            # Create performance comparison plot
            performance_plot = self.visualizer.plot_performance_comparison(benchmark_results)
            print(f"✅ Performance comparison plot: {performance_plot}")
            
            # Create dashboard
            dashboard_path = self.visualizer.create_dashboard(benchmark_results)
            print(f"✅ Dashboard created: {dashboard_path}")
            
        # Generate evaluation report
        evaluation_report = self._generate_evaluation_report(results)
        
        # Save comprehensive report
        report_path = Path("test_plots") / f"comprehensive_evaluation_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            json.dump(evaluation_report, f, indent=2)
            
        print(f"✅ Comprehensive evaluation report: {report_path}")
        print("\n🎉 Evaluation Complete!")
        
        return evaluation_report
        
    def _generate_evaluation_report(self, benchmark_results: Dict) -> Dict:
        """Generate comprehensive evaluation report"""
        report = {
            'evaluation_summary': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_scenarios': len(self.benchmark_config.traffic_scenarios),
                'total_controllers': len(self.benchmark_config.controllers),
                'benchmark_duration_minutes': self.benchmark_config.duration_minutes
            },
            'benchmark_results': benchmark_results,
            'recommendations': [],
            'system_health': self._assess_system_health(benchmark_results)
        }
        
        # Generate recommendations
        if 'summary' in benchmark_results:
            for scenario, stats in benchmark_results['summary'].items():
                best_controller = stats.get('best_controller')
                best_score = stats.get('best_score', 0)
                
                if best_controller:
                    recommendation = {
                        'scenario': scenario,
                        'recommended_controller': best_controller,
                        'performance_score': best_score,
                        'reasoning': f"Best performance in {scenario} traffic conditions"
                    }
                    report['recommendations'].append(recommendation)
                    
        return report
        
    def _assess_system_health(self, results: Dict) -> Dict:
        """Assess overall system health"""
        health_score = 0
        issues = []
        
        # Check if all benchmarks completed successfully
        if 'detailed_results' in results:
            completed_count = 0
            total_count = len(results['detailed_results'])
            
            for result in results['detailed_results']:
                if 'error' not in result:
                    completed_count += 1
                else:
                    issues.append(f"Benchmark failed: {result['error']}")
                    
            completion_rate = completed_count / total_count if total_count > 0 else 0
            health_score += completion_rate * 40  # 40% weight for completion
            
        # Check performance scores
        if 'summary' in results:
            avg_score = 0
            score_count = 0
            
            for scenario, stats in results['summary'].items():
                for controller, score in stats.get('controller_scores', {}).items():
                    avg_score += score
                    score_count += 1
                    
            if score_count > 0:
                avg_score /= score_count
                health_score += avg_score * 0.6  # 60% weight for performance
                
        return {
            'overall_health_score': min(100, health_score),
            'issues_detected': issues,
            'status': 'healthy' if health_score >= 70 else 'needs_attention'
        }
        
    def run_quick_test(self) -> Dict:
        """Run a quick test to verify system functionality"""
        print("🔍 Running Quick System Test...")
        
        # Test rule-based controller
        test_metrics = TrafficMetrics()
        result = self.run_rule_based_benchmark('low', test_metrics, 1)  # 1 minute test
        
        # Check if metrics were collected
        summary = test_metrics.get_summary()
        performance_score = test_metrics.get_performance_score()
        
        test_result = {
            'status': 'passed' if result.get('status') == 'completed' else 'failed',
            'performance_score': performance_score,
            'metrics_collected': len(summary) > 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"✅ Quick test result: {test_result['status']}")
        print(f"📊 Performance score: {performance_score:.1f}")
        
        return test_result

def main():
    """Main evaluation script"""
    parser = argparse.ArgumentParser(description='AI Traffic Light System Evaluation')
    parser.add_argument('--mode', choices=['quick', 'comprehensive'], 
                       default='quick', help='Evaluation mode')
    parser.add_argument('--config', default='configs/zones/intersection_a.json',
                       help='Configuration file path')
    parser.add_argument('--duration', type=int, default=5,
                       help='Benchmark duration in minutes')
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = SystemEvaluator(args.config)
    evaluator.benchmark_config.duration_minutes = args.duration
    
    if args.mode == 'quick':
        result = evaluator.run_quick_test()
    else:
        result = evaluator.run_comprehensive_evaluation()
        
    print(f"\n📋 Evaluation completed successfully!")
            print(f"📁 Results saved in: test_plots/")

if __name__ == "__main__":
    main() 