#!/usr/bin/env python3
"""Benchmark Runner for Traffic Light Control Strategies"""

import time
import json
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
import threading
from concurrent.futures import ThreadPoolExecutor

from .metrics import TrafficMetrics

@dataclass
class BenchmarkConfig:
    """Configuration for benchmark runs"""
    duration_minutes: int = 10
    traffic_scenarios: List[str] = None
    controllers: List[str] = None
    metrics_interval: float = 1.0  # seconds
    save_results: bool = True
    output_dir: str = "benchmark_results"
    
    def __post_init__(self):
        if self.traffic_scenarios is None:
            self.traffic_scenarios = ['low', 'medium', 'high']
        if self.controllers is None:
            self.controllers = ['rule-based', 'rl-agent']

class BenchmarkRunner:
    """Benchmark runner for comparing traffic control strategies"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results = {}
        self.metrics_collector = TrafficMetrics()
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def run_benchmark(self, controller_func: Callable, scenario_name: str, 
                     controller_name: str) -> Dict:
        """Run a single benchmark test"""
        print(f"Running benchmark: {controller_name} on {scenario_name} scenario")
        
        # Reset metrics
        self.metrics_collector.reset()
        
        # Start benchmark
        start_time = time.time()
        end_time = start_time + (self.config.duration_minutes * 60)
        
        # Run controller function with metrics collection
        try:
            controller_func(
                scenario_name=scenario_name,
                metrics_collector=self.metrics_collector,
                duration_minutes=self.config.duration_minutes
            )
        except Exception as e:
            print(f"Benchmark failed: {e}")
            return {'error': str(e)}
            
        # Calculate final metrics
        final_metrics = self.metrics_collector.get_summary()
        performance_score = self.metrics_collector.get_performance_score()
        
        benchmark_result = {
            'scenario': scenario_name,
            'controller': controller_name,
            'duration_minutes': self.config.duration_minutes,
            'performance_score': performance_score,
            'metrics': final_metrics,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return benchmark_result
        
    def run_comparison(self, controller_functions: Dict[str, Callable]):
        """Run comparison benchmarks for all controllers and scenarios"""
        all_results = []
        
        for scenario in self.config.traffic_scenarios:
            for controller_name, controller_func in controller_functions.items():
                result = self.run_benchmark(controller_func, scenario, controller_name)
                all_results.append(result)
                
                # Save individual result
                if self.config.save_results:
                    filename = f"{controller_name}_{scenario}_{int(time.time())}.json"
                    filepath = self.output_dir / filename
                    with open(filepath, 'w') as f:
                        json.dump(result, f, indent=2)
                        
        # Generate comparison report
        comparison_report = self.generate_comparison_report(all_results)
        
        # Save comparison report
        if self.config.save_results:
            report_path = self.output_dir / f"comparison_report_{int(time.time())}.json"
            with open(report_path, 'w') as f:
                json.dump(comparison_report, f, indent=2)
                
        return comparison_report
        
    def generate_comparison_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive comparison report"""
        report = {
            'summary': {},
            'detailed_results': results,
            'recommendations': []
        }
        
        # Group results by scenario
        scenario_results = {}
        for result in results:
            if 'error' in result:
                continue
            scenario = result['scenario']
            if scenario not in scenario_results:
                scenario_results[scenario] = []
            scenario_results[scenario].append(result)
            
        # Calculate summary statistics
        summary_stats = {}
        for scenario, scenario_data in scenario_results.items():
            summary_stats[scenario] = {
                'best_controller': None,
                'best_score': 0,
                'controller_scores': {},
                'improvement_over_baseline': {}
            }
            
            for result in scenario_data:
                controller = result['controller']
                score = result['performance_score']
                
                summary_stats[scenario]['controller_scores'][controller] = score
                
                if score > summary_stats[scenario]['best_score']:
                    summary_stats[scenario]['best_score'] = score
                    summary_stats[scenario]['best_controller'] = controller
                    
        # Calculate improvements over baseline (rule-based)
        for scenario, stats in summary_stats.items():
            baseline_score = stats['controller_scores'].get('rule-based', 0)
            for controller, score in stats['controller_scores'].items():
                if controller != 'rule-based' and baseline_score > 0:
                    improvement = ((score - baseline_score) / baseline_score) * 100
                    stats['improvement_over_baseline'][controller] = improvement
                    
        report['summary'] = summary_stats
        
        # Generate recommendations
        recommendations = []
        for scenario, stats in summary_stats.items():
            best_controller = stats['best_controller']
            best_score = stats['best_score']
            
            if best_controller and best_controller != 'rule-based':
                improvement = stats['improvement_over_baseline'].get(best_controller, 0)
                recommendations.append({
                    'scenario': scenario,
                    'recommendation': f"Use {best_controller} for {scenario} traffic",
                    'reasoning': f"Best performance score: {best_score:.1f} "
                                f"(+{improvement:.1f}% over baseline)"
                })
            else:
                recommendations.append({
                    'scenario': scenario,
                    'recommendation': f"Use rule-based controller for {scenario} traffic",
                    'reasoning': f"Best performance score: {best_score:.1f}"
                })
                
        report['recommendations'] = recommendations
        
        return report
        
    def run_stress_test(self, controller_func: Callable, duration_hours: int = 12):
        """Run extended stress test"""
        print(f"Running stress test for {duration_hours} hours...")
        
        self.metrics_collector.reset()
        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)
        
        # Monitor for frame drops and errors
        error_count = 0
        frame_drops = 0
        last_fps = 0
        
        try:
            while time.time() < end_time:
                current_time = time.time()
                
                # Run controller for a short interval
                try:
                    controller_func(
                        scenario_name='stress_test',
                        metrics_collector=self.metrics_collector,
                        duration_minutes=1
                    )
                except Exception as e:
                    error_count += 1
                    print(f"Stress test error {error_count}: {e}")
                    
                # Check for frame drops
                current_fps = self.metrics_collector.fps
                if current_fps < 10 and last_fps >= 10:  # Significant drop
                    frame_drops += 1
                last_fps = current_fps
                
                # Save intermediate results every hour
                if int(current_time - start_time) % 3600 == 0:
                    self.save_stress_test_checkpoint(current_time - start_time)
                    
        except KeyboardInterrupt:
            print("Stress test interrupted by user")
            
        # Final stress test report
        stress_report = {
            'duration_hours': duration_hours,
            'total_errors': error_count,
            'frame_drops': frame_drops,
            'final_metrics': self.metrics_collector.get_summary(),
            'stability_score': self.calculate_stability_score(error_count, frame_drops)
        }
        
        # Save stress test results
        stress_file = self.output_dir / f"stress_test_{int(time.time())}.json"
        with open(stress_file, 'w') as f:
            json.dump(stress_report, f, indent=2)
            
        return stress_report
        
    def save_stress_test_checkpoint(self, elapsed_time: float):
        """Save checkpoint during stress test"""
        checkpoint = {
            'elapsed_time': elapsed_time,
            'metrics': self.metrics_collector.get_summary()
        }
        
        checkpoint_file = self.output_dir / f"stress_checkpoint_{int(elapsed_time)}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
            
    def calculate_stability_score(self, error_count: int, frame_drops: int) -> float:
        """Calculate stability score (0-100)"""
        # Penalize errors and frame drops
        error_penalty = min(50, error_count * 5)  # Max 50 point penalty for errors
        frame_drop_penalty = min(30, frame_drops * 2)  # Max 30 point penalty for frame drops
        
        stability_score = 100 - error_penalty - frame_drop_penalty
        return max(0, stability_score)
        
    def load_previous_results(self) -> List[Dict]:
        """Load previous benchmark results"""
        results = []
        for file in self.output_dir.glob("*.json"):
            if file.name.startswith("comparison_report"):
                continue
            try:
                with open(file, 'r') as f:
                    result = json.load(f)
                    results.append(result)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        return results 