import time
import json
import numpy as np
from pathlib import Path
from gymnasium import spaces  # Correct import
from gymnasium import Env
import gymnasium as gym

class TrafficLightEnv(Env):  # Inherit from Env directly
    def __init__(self, config_path: str = "configs/zones/intersection_a.json", max_steps: int = 100):
        super().__init__()
        
        # STATE SPACE (Properly shaped Box spaces)
        self.observation_space = spaces.Dict({
            'zone_counts': spaces.Box(low=0, high=50, shape=(4,), dtype=np.int32),
            'current_phase': spaces.Box(low=0, high=3, shape=(1,), dtype=np.int32),
            'elapsed_time': spaces.Box(low=0, high=30, shape=(1,), dtype=np.float32)
        })

        # ACTION SPACE (Box format)
        self.action_space = spaces.Box(
            low=np.array([0, 5], dtype=np.float32),    # [direction, duration]
            high=np.array([3, 30], dtype=np.float32),
            dtype=np.float32
        )

        # Initialize tracking variables
        self.max_steps = max_steps
        self._step_count = 0
        self._data_path = Path(config_path)
        self._current_counts = np.zeros(4, dtype=np.int32)
        self._prev_counts = np.zeros(4, dtype=np.int32)
        self._current_phase = 0
        self._elapsed = 0.0
        self._last_update = time.time()

    def _load_zone_counts(self) -> np.ndarray:
        """Safely load and convert zone counts with comprehensive type handling"""
        try:
            with open(self._data_path) as f:
                data = json.load(f)
                
            counts = []
            for zone in ["Zone A", "Zone B", "Zone C", "Zone D"]:
                value = data.get(zone, 0)
                
                # Handle list/array inputs by taking the first element
                if isinstance(value, (list, np.ndarray)):
                    value = value[0] if len(value) > 0 else 0
                
                # Convert to integer safely
                try:
                    count = int(float(value))  # Handles strings and floats
                except (ValueError, TypeError):
                    count = 0
                    
                counts.append(min(max(count, 0), 50))  # Clip to 0-50 range
                
            return np.array(counts, dtype=np.int32)
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return np.zeros(4, dtype=np.int32)

    def reset(self, *, seed=None, options=None):
        """Ensure proper observation shapes on reset"""
        super().reset(seed=seed)
        self._step_count = 0
        self._current_counts = self._load_zone_counts()
        self._prev_counts = self._current_counts.copy()
        self._current_phase = 0
        self._elapsed = 0.0
        self._last_update = time.time()
        return self._get_state(), {}

    def step(self, action: np.ndarray):
        """Execute one time step"""
        # Convert action
        direction = int(np.clip(action[0], 0, 3))
        duration = float(np.clip(action[1], 5, 30))
        
        # Update state
        self._current_counts = self._load_zone_counts()
        reward = self._calculate_reward(direction)
        
        # Update tracking
        self._prev_counts[:] = self._current_counts
        self._current_phase = direction
        self._elapsed = duration
        self._step_count += 1
        self._last_update = time.time()
        
        # Check termination
        truncated = self._step_count >= self.max_steps
        return self._get_state(), reward, False, truncated, {}

    def _calculate_reward(self, new_phase: int) -> float:
        """Compute reward in O(1) time"""
        cleared = max(0, self._prev_counts[new_phase] - self._current_counts[new_phase])
        wait_penalty = 0.1 * np.sum(self._current_counts)
        change_penalty = 0.5 if new_phase != self._current_phase else 0
        return (cleared * 2.0) - wait_penalty - change_penalty

    def _get_state(self) -> dict:
        """Ensure proper observation shapes"""
        return {
            'zone_counts': np.array(self._current_counts, dtype=np.int32),
            'current_phase': np.array([self._current_phase], dtype=np.int32),
            'elapsed_time': np.array([self._elapsed], dtype=np.float32)
        }

    def render(self):
        """Optional rendering"""
        state = self._get_state()
        print(f"Phase: {['N','E','S','W'][state['current_phase']]} | "
              f"Counts: {state['zone_counts']} | "
              f"Elapsed: {state['elapsed_time']:.1f}s")