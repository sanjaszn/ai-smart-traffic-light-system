#!/usr/bin/env python3
"""
RL Traffic Controller - Bridges trained RL agent with live simulation
Connects the trained PPO agent to the traffic simulation for real-time control
"""

import numpy as np
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class RLTrafficController:
    """
    RL Traffic Controller - Connects trained RL agent to live simulation
    
    This controller acts as a bridge between the trained RL agent and the
    live traffic simulation, handling:
    - State conversion (simulation state → RL state)
    - Action interpretation (RL action → traffic light decision)
    - Model loading and prediction
    """
    
    def __init__(self, model_path: Optional[str] = None, verbose: bool = True):
        """
        Initialize RL Traffic Controller
        
        Args:
            model_path: Path to trained PPO model (.zip file)
            verbose: Enable debug logging
        """
        self.verbose = verbose
        self.agent = None
        self.model_path = model_path
        self.last_action = None
        self.last_state = None
        self.action_history = []
        
        # Direction mapping (RL action → simulation direction)
        self.direction_map = {
            0: 'South',   # Zone A
            1: 'East',    # Zone B  
            2: 'North',   # Zone C
            3: 'West'     # Zone D
        }
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            if verbose:
                print("⚠️  No trained model provided - using random actions")
    
    def load_model(self, model_path: str) -> bool:
        """
        Load trained PPO model from file
        
        Args:
            model_path: Path to .zip model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.verbose:
                print(f"🤖 Loading RL model from: {model_path}")
            
            # Load the trained agent
            self.agent = PPO.load(model_path)
            
            if self.verbose:
                print("✅ RL model loaded successfully!")
                
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to load RL model: {e}")
            return False
    
    def get_action(self, simulation_state: Dict[str, Any]) -> Tuple[str, float]:
        """
        Get traffic light action from RL agent
        
        Args:
            simulation_state: Current simulation state with zone counts
            
        Returns:
            Tuple of (direction, duration) for traffic light control
        """
        # Convert simulation state to RL state format
        rl_state = self._convert_to_rl_state(simulation_state)
        
        if self.agent is None:
            # Fallback to random action if no model loaded
            direction_idx = np.random.randint(0, 4)
            duration = np.random.uniform(5.0, 15.0)
        else:
            # Get action from trained agent
            action, _ = self.agent.predict(rl_state, deterministic=True)
            direction_idx = int(np.clip(action[0], 0, 3))
            duration = float(np.clip(action[1], 5.0, 30.0))
        
        # Convert to simulation format
        direction = self.direction_map[direction_idx]
        
        # Store for debugging
        self.last_action = (direction, duration)
        self.last_state = simulation_state
        self.action_history.append({
            'timestamp': time.time(),
            'state': simulation_state,
            'action': (direction, duration),
            'direction_idx': direction_idx
        })
        
        if self.verbose:
            print(f"🧠 RL Action: {direction} for {duration:.1f}s (idx: {direction_idx})")
        
        return direction, duration
    
    def _convert_to_rl_state(self, simulation_state: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """
        Convert simulation state to RL environment state format
        
        Args:
            simulation_state: Simulation state with zone counts
            
        Returns:
            RL state dictionary matching environment format
        """
        # Extract zone counts in correct order: [South, East, North, West]
        zone_counts = [
            simulation_state.get('South', 0),
            simulation_state.get('East', 0), 
            simulation_state.get('North', 0),
            simulation_state.get('West', 0)
        ]
        
        # Get current phase (0-3) - default to 0 if not specified
        current_phase = simulation_state.get('current_phase', 0)
        
        # Get elapsed time - default to 0 if not specified
        elapsed_time = simulation_state.get('elapsed_time', 0.0)
        
        # Convert to RL state format
        rl_state = {
            'zone_counts': np.array(zone_counts, dtype=np.int32),
            'current_phase': np.array([current_phase], dtype=np.int32),
            'elapsed_time': np.array([elapsed_time], dtype=np.float32)
        }
        
        return rl_state
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get controller statistics for monitoring
        
        Returns:
            Dictionary with controller stats
        """
        if not self.action_history:
            return {'total_actions': 0, 'model_loaded': self.agent is not None}
        
        recent_actions = self.action_history[-10:]  # Last 10 actions
        
        # Analyze action distribution
        directions = [action['action'][0] for action in recent_actions]
        durations = [action['action'][1] for action in recent_actions]
        
        direction_counts = {}
        for direction in directions:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        return {
            'total_actions': len(self.action_history),
            'model_loaded': self.agent is not None,
            'recent_direction_distribution': direction_counts,
            'avg_duration': np.mean(durations),
            'last_action': self.last_action,
            'last_action_time': self.action_history[-1]['timestamp'] if self.action_history else None
        }
    
    def reset(self):
        """Reset controller state"""
        self.last_action = None
        self.last_state = None
        self.action_history = []
        if self.verbose:
            print("🔄 RL Controller reset")


def create_rl_controller(model_path: Optional[str] = None, verbose: bool = True) -> RLTrafficController:
    """
    Factory function to create RL Traffic Controller
    
    Args:
        model_path: Path to trained model
        verbose: Enable debug logging
        
    Returns:
        Configured RL Traffic Controller
    """
    return RLTrafficController(model_path=model_path, verbose=verbose)


if __name__ == "__main__":
    """Test the RL Controller"""
    print("🧪 Testing RL Traffic Controller")
    
    # Create controller without model (will use random actions)
    controller = RLTrafficController(verbose=True)
    
    # Test state conversion
    test_state = {
        'South': 5,
        'East': 3, 
        'North': 8,
        'West': 2,
        'current_phase': 1,
        'elapsed_time': 10.5
    }
    
    print(f"\n📊 Test State: {test_state}")
    
    # Get action
    direction, duration = controller.get_action(test_state)
    print(f"🎯 Action: {direction} for {duration:.1f}s")
    
    # Get stats
    stats = controller.get_stats()
    print(f"📈 Stats: {stats}")
    
    print("\n✅ RL Controller test completed!") 