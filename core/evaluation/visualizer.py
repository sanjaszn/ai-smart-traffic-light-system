#!/usr/bin/env python3
"""Metrics Visualizer for Traffic Light System Evaluation"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class MetricsVisualizer:
    """Visualization tools for traffic metrics and benchmark results"""
    
    def __init__(self, output_dir: str = "evaluation_plots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def plot_performance_comparison(self, benchmark_results: List[Dict], 
                                  save_plot: bool = True) -> str:
        """Create performance comparison plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Traffic Light Control Performance Comparison', fontsize=16, fontweight='bold')
        
        # Extract data
        scenarios = []
        controllers = []
        scores = []
        throughput = []
        wait_times = []
        
        for result in benchmark_results:
            if 'error' in result:
                continue
            scenarios.append(result['scenario'])
            controllers.append(result['controller'])
            scores.append(result['performance_score'])
            
            metrics = result['metrics']
            throughput.append(metrics['core_metrics']['vehicles_cleared_per_minute'])
            
            # Average wait time across lanes
            avg_wait = np.mean(list(metrics['core_metrics']['average_wait_time_per_lane'].values()))
            wait_times.append(avg_wait)
            
        # Create DataFrame for easier plotting
        df = pd.DataFrame({
            'Scenario': scenarios,
            'Controller': controllers,
            'Performance Score': scores,
            'Throughput': throughput,
            'Avg Wait Time': wait_times
        })
        
        # 1. Performance Score by Scenario and Controller
        ax1 = axes[0, 0]
        pivot_score = df.pivot(index='Scenario', columns='Controller', values='Performance Score')
        pivot_score.plot(kind='bar', ax=ax1, width=0.8)
        ax1.set_title('Performance Score Comparison')
        ax1.set_ylabel('Performance Score (0-100)')
        ax1.legend(title='Controller')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Throughput Comparison
        ax2 = axes[0, 1]
        pivot_throughput = df.pivot(index='Scenario', columns='Controller', values='Throughput')
        pivot_throughput.plot(kind='bar', ax=ax2, width=0.8)
        ax2.set_title('Vehicles Cleared per Minute')
        ax2.set_ylabel('Vehicles/Minute')
        ax2.legend(title='Controller')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Wait Time Comparison
        ax3 = axes[1, 0]
        pivot_wait = df.pivot(index='Scenario', columns='Controller', values='Avg Wait Time')
        pivot_wait.plot(kind='bar', ax=ax3, width=0.8)
        ax3.set_title('Average Wait Time per Lane')
        ax3.set_ylabel('Wait Time (seconds)')
        ax3.legend(title='Controller')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Overall Performance Heatmap
        ax4 = axes[1, 1]
        heatmap_data = df.pivot(index='Scenario', columns='Controller', values='Performance Score')
        sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax4)
        ax4.set_title('Performance Score Heatmap')
        
        plt.tight_layout()
        
        if save_plot:
            plot_path = self.output_dir / f"performance_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(plot_path)
        else:
            plt.show()
            return ""
            
    def plot_metrics_timeline(self, metrics_history: List[Dict], 
                            save_plot: bool = True) -> str:
        """Plot metrics over time"""
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle('Traffic Metrics Timeline', fontsize=16, fontweight='bold')
        
        # Extract timeline data
        timestamps = []
        throughput = []
        wait_times = []
        queue_lengths = []
        rewards = []
        fps_values = []
        
        for entry in metrics_history:
            timestamps.append(entry.get('timestamp', len(timestamps)))
            metrics = entry['metrics']
            
            throughput.append(metrics['core_metrics']['vehicles_cleared_per_minute'])
            
            # Average wait time
            avg_wait = np.mean(list(metrics['core_metrics']['average_wait_time_per_lane'].values()))
            wait_times.append(avg_wait)
            
            # Average queue length
            avg_queue = np.mean(list(metrics['quality_metrics']['queue_length_per_lane'].values()))
            queue_lengths.append(avg_queue)
            
            # RL reward
            rewards.append(metrics['rl_metrics']['avg_reward'])
            
            # FPS
            fps_values.append(metrics['system_metrics']['fps'])
            
        # 1. Throughput over time
        axes[0, 0].plot(timestamps, throughput, marker='o', linewidth=2)
        axes[0, 0].set_title('Throughput Over Time')
        axes[0, 0].set_ylabel('Vehicles/Minute')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Wait time over time
        axes[0, 1].plot(timestamps, wait_times, marker='s', linewidth=2, color='orange')
        axes[0, 1].set_title('Average Wait Time Over Time')
        axes[0, 1].set_ylabel('Wait Time (seconds)')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Queue length over time
        axes[1, 0].plot(timestamps, queue_lengths, marker='^', linewidth=2, color='green')
        axes[1, 0].set_title('Average Queue Length Over Time')
        axes[1, 0].set_ylabel('Queue Length')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. RL Reward over time
        axes[1, 1].plot(timestamps, rewards, marker='d', linewidth=2, color='red')
        axes[1, 1].set_title('RL Reward Over Time')
        axes[1, 1].set_ylabel('Average Reward')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 5. FPS over time
        axes[2, 0].plot(timestamps, fps_values, marker='*', linewidth=2, color='purple')
        axes[2, 0].set_title('System FPS Over Time')
        axes[2, 0].set_ylabel('FPS')
        axes[2, 0].set_xlabel('Time')
        axes[2, 0].grid(True, alpha=0.3)
        
        # 6. Performance score over time
        performance_scores = []
        for entry in metrics_history:
            # Calculate performance score from metrics
            score = self._calculate_performance_score_from_metrics(entry['metrics'])
            performance_scores.append(score)
            
        axes[2, 1].plot(timestamps, performance_scores, marker='o', linewidth=2, color='brown')
        axes[2, 1].set_title('Overall Performance Score Over Time')
        axes[2, 1].set_ylabel('Performance Score (0-100)')
        axes[2, 1].set_xlabel('Time')
        axes[2, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            plot_path = self.output_dir / f"metrics_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(plot_path)
        else:
            plt.show()
            return ""
            
    def plot_lane_analysis(self, metrics: Dict, save_plot: bool = True) -> str:
        """Detailed lane-by-lane analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Lane-by-Lane Traffic Analysis', fontsize=16, fontweight='bold')
        
        core_metrics = metrics['core_metrics']
        quality_metrics = metrics['quality_metrics']
        
        # Extract lane data
        lanes = list(core_metrics['average_wait_time_per_lane'].keys())
        wait_times = list(core_metrics['average_wait_time_per_lane'].values())
        queue_lengths = list(quality_metrics['queue_length_per_lane'].values())
        starvation_counts = list(core_metrics['starvation_detection'].values())
        
        # 1. Wait time by lane
        axes[0, 0].bar(lanes, wait_times, color='skyblue', alpha=0.7)
        axes[0, 0].set_title('Average Wait Time by Lane')
        axes[0, 0].set_ylabel('Wait Time (seconds)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Queue length by lane
        axes[0, 1].bar(lanes, queue_lengths, color='lightcoral', alpha=0.7)
        axes[0, 1].set_title('Current Queue Length by Lane')
        axes[0, 1].set_ylabel('Queue Length')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 3. Starvation incidents by lane
        axes[1, 0].bar(lanes, starvation_counts, color='gold', alpha=0.7)
        axes[1, 0].set_title('Starvation Incidents by Lane')
        axes[1, 0].set_ylabel('Starvation Count')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. Lane utilization pie chart
        lane_utilization = metrics['efficiency_metrics']['lane_utilization']
        if lane_utilization:
            util_lanes = list(lane_utilization.keys())
            util_values = list(lane_utilization.values())
            
            # Only show lanes with utilization > 0
            non_zero_indices = [i for i, v in enumerate(util_values) if v > 0]
            util_lanes = [util_lanes[i] for i in non_zero_indices]
            util_values = [util_values[i] for i in non_zero_indices]
            
            if util_values:
                axes[1, 1].pie(util_values, labels=util_lanes, autopct='%1.1f%%', startangle=90)
                axes[1, 1].set_title('Lane Utilization Distribution')
        
        plt.tight_layout()
        
        if save_plot:
            plot_path = self.output_dir / f"lane_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(plot_path)
        else:
            plt.show()
            return ""
            
    def plot_rl_analysis(self, metrics: Dict, save_plot: bool = True) -> str:
        """RL-specific analysis plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Reinforcement Learning Analysis', fontsize=16, fontweight='bold')
        
        rl_metrics = metrics['rl_metrics']
        
        # 1. Action distribution
        actions = list(rl_metrics['action_distribution'].keys())
        action_counts = list(rl_metrics['action_distribution'].values())
        
        if actions:
            axes[0, 0].bar(actions, action_counts, color='lightgreen', alpha=0.7)
            axes[0, 0].set_title('Action Distribution')
            axes[0, 0].set_xlabel('Action')
            axes[0, 0].set_ylabel('Count')
        
        # 2. Reward distribution (if we have reward history)
        if 'reward_history' in rl_metrics and rl_metrics['reward_history']:
            rewards = rl_metrics['reward_history']
            axes[0, 1].hist(rewards, bins=20, color='lightblue', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('Reward Distribution')
            axes[0, 1].set_xlabel('Reward')
            axes[0, 1].set_ylabel('Frequency')
        
        # 3. Exploration rate over time (placeholder)
        axes[1, 0].text(0.5, 0.5, f"Exploration Rate: {rl_metrics['exploration_rate']:.3f}", 
                       ha='center', va='center', transform=axes[1, 0].transAxes, fontsize=14)
        axes[1, 0].set_title('Current Exploration Rate')
        axes[1, 0].axis('off')
        
        # 4. Average reward trend
        avg_reward = rl_metrics['avg_reward']
        axes[1, 1].bar(['Average Reward'], [avg_reward], color='orange', alpha=0.7)
        axes[1, 1].set_title('Average Reward')
        axes[1, 1].set_ylabel('Reward Value')
        
        plt.tight_layout()
        
        if save_plot:
            plot_path = self.output_dir / f"rl_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(plot_path)
        else:
            plt.show()
            return ""
            
    def create_dashboard(self, benchmark_results: List[Dict], 
                        metrics_history: List[Dict] = None) -> str:
        """Create comprehensive dashboard with all plots"""
        dashboard_path = self.output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Generate all plots
        performance_plot = self.plot_performance_comparison(benchmark_results, save_plot=True)
        
        plots = [performance_plot]
        if metrics_history:
            timeline_plot = self.plot_metrics_timeline(metrics_history, save_plot=True)
            plots.append(timeline_plot)
            
        # Create HTML dashboard
        html_content = self._generate_dashboard_html(plots, benchmark_results)
        
        with open(dashboard_path, 'w') as f:
            f.write(html_content)
            
        return str(dashboard_path)
        
    def _calculate_performance_score_from_metrics(self, metrics: Dict) -> float:
        """Calculate performance score from metrics dictionary"""
        # Simplified calculation - can be enhanced
        throughput = metrics['core_metrics']['vehicles_cleared_per_minute']
        avg_wait = np.mean(list(metrics['core_metrics']['average_wait_time_per_lane'].values()))
        fps = metrics['system_metrics']['fps']
        
        # Simple scoring
        throughput_score = min(100, throughput * 10)
        wait_score = max(0, 100 - avg_wait * 2)
        fps_score = min(100, fps * 2)
        
        return (throughput_score * 0.4 + wait_score * 0.4 + fps_score * 0.2)
        
    def _generate_dashboard_html(self, plot_paths: List[str], results: List[Dict]) -> str:
        """Generate HTML dashboard"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Traffic Light System Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; margin-bottom: 30px; }
                .plot-section { margin: 30px 0; }
                .plot-section h2 { color: #333; border-bottom: 2px solid #007acc; }
                .plot-section img { max-width: 100%; height: auto; border: 1px solid #ddd; }
                .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; }
                .metric { display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚦 AI Traffic Light System Dashboard</h1>
                <p>Performance Evaluation and Benchmarking Results</p>
            </div>
        """
        
        # Add summary statistics
        if results:
            html += '<div class="summary"><h2>Summary Statistics</h2>'
            for result in results:
                if 'error' not in result:
                    html += f"""
                    <div class="metric">
                        <strong>{result['controller']} - {result['scenario']}</strong><br>
                        Performance Score: {result['performance_score']:.1f}<br>
                        Throughput: {result['metrics']['core_metrics']['vehicles_cleared_per_minute']:.1f} vehicles/min
                    </div>
                    """
            html += '</div>'
        
        # Add plots
        for i, plot_path in enumerate(plot_paths):
            plot_name = Path(plot_path).stem.replace('_', ' ').title()
            html += f"""
            <div class="plot-section">
                <h2>{plot_name}</h2>
                <img src="{plot_path}" alt="{plot_name}">
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html 