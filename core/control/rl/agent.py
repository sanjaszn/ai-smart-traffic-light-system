import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from typing import Any

class TensorboardCallback(BaseCallback):
    """Enhanced callback with traffic-specific metrics"""
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self._eval_freq = 1000
        
    def _on_step(self) -> bool:
        if self.n_calls % self._eval_freq == 0:
            # Log traffic distribution and phase efficiency
            counts = self.training_env.get_attr('_current_counts')[0]
            phase = self.training_env.get_attr('_current_phase')[0]
            
            for i, zone in enumerate(['North', 'East', 'South', 'West']):
                self.logger.record(f"zones/{zone}", counts[i])
            
            self.logger.record("phase/current", phase)
            self.logger.record("phase/elapsed", 
                             self.training_env.get_attr('_elapsed')[0])
        return True

def build_agent(env, **kwargs):
    params = {
        'policy': 'MultiInputPolicy',  # Must use this for Dict observations
        'policy_kwargs': {
            'net_arch': dict(pi=[64, 64], vf=[64, 64])  # Optional: Custom network
        },
        'learning_rate': 3e-4,
        'n_steps': 256,
        'batch_size': 64,
        **kwargs
    }
    return PPO(env=env, **params)