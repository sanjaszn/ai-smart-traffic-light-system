import pytest
import numpy as np
import gymnasium as gym
import gymnasium as spaces
from core.control.rl.env import TrafficLightEnv

@pytest.fixture
def env():
    """Fixture providing a clean environment instance"""
    return TrafficLightEnv(max_steps=10)

def test_observation_space(env):
    """Validate state vector structure and bounds"""
    obs_space = env.observation_space
    
    # Check types and shapes
    assert isinstance(obs_space, spaces.Dict)
    assert isinstance(obs_space['zone_counts'], spaces.Box)
    assert obs_space['zone_counts'].shape == (4,)
    assert obs_space['current_phase'].n == 4
    assert isinstance(obs_space['elapsed_time'], spaces.Box)
    
    # Test bounds enforcement
    test_obs = obs_space.sample()
    assert np.all(0 <= test_obs['zone_counts']) 
    assert np.all(test_obs['zone_counts'] <= 50)
    assert 0 <= test_obs['current_phase'] <= 3
    assert 0 <= test_obs['elapsed_time'] <= 30

def test_action_space(env):
    """Validate action structure and bounds"""
    action_space = env.action_space
    
    assert isinstance(action_space, spaces.Dict)
    assert action_space['direction'].n == 4
    assert isinstance(action_space['duration'], spaces.Box)
    assert action_space['duration'].low == 5
    assert action_space['duration'].high == 30

def test_reset(env):
    """Test environment initialization"""
    obs, info = env.reset()
    
    assert isinstance(obs, dict)
    assert set(obs.keys()) == {'zone_counts', 'current_phase', 'elapsed_time'}
    assert obs['zone_counts'].shape == (4,)
    assert obs['current_phase'] == 0  # Starts at North
    assert obs['elapsed_time'] == 0.0

def test_step(env):
    """Validate single transition"""
    env.reset()
    action = {'direction': 1, 'duration': 10.0}  # East for 10s
    
    obs, reward, terminated, truncated, info = env.step(action)
    
    # State updates
    assert obs['current_phase'] == 1  # East
    assert obs['elapsed_time'] == 10.0
    assert not terminated  # Only truncation ends episodes
    
    # Reward sanity checks
    assert isinstance(reward, float)
    assert -10 <= reward <= 20  # Based on your reward function

def test_truncation(env):
    """Test max steps termination"""
    env.reset()
    for _ in range(9):
        _, _, _, truncated, _ = env.step({'direction': 0, 'duration': 5})
        assert not truncated
    
    # 10th step should truncate
    _, _, _, truncated, _ = env.step({'direction': 0, 'duration': 5})
    assert truncated

def test_reward_logic(env):
    """Verify reward calculation matches spec"""
    env.reset()
    
    # Force known state
    env._current_counts = np.array([10, 5, 2, 0])  # North busiest
    env._prev_counts = np.array([12, 5, 2, 0])     # 2 cars cleared
    
    action = {'direction': 0, 'duration': 10}  # North
    _, reward, _, _, _ = env.step(action)
    
    # reward = (cleared * 2.0) - (wait_penalty * 0.1) - change_penalty
    expected = (2 * 2.0) - (sum([10,5,2,0]) * 0.1) - 0
    assert np.isclose(reward, expected)

def test_o1_memory(env):
    """Validates O(1) memory usage with realistic thresholds"""
    import tracemalloc
    import gc

    # Warm-up and baseline measurement
    env.reset()
    for _ in range(10):
        env.step({'direction': 0, 'duration': 5})
    gc.collect()  # Force clean up

    # Measurement phase
    tracemalloc.start()
    initial = tracemalloc.get_traced_memory()[0]
    
    # Test loop
    for _ in range(100):
        env.step({'direction': 0, 'duration': 5})
    
    used = tracemalloc.get_traced_memory()[0] - initial
    tracemalloc.stop()

    # Adjusted threshold for Windows/Python overhead
    assert used < 5120, f"Memory grew by {used} bytes (>5KB limit)"

def test_one_pass_step(env, mocker):
    """Ensure no redundant calculations"""
    # Mock the reward calculator
    mock_reward = mocker.patch.object(env, '_calculate_reward', return_value=0.0)
    
    env.reset()
    env.step({'direction': 1, 'duration': 10})
    
    mock_reward.assert_called_once()  # Should be called exactly once

def test_space_types():
    env = TrafficLightEnv()
    assert isinstance(env.observation_space, gym.spaces.Dict)
    assert isinstance(env.action_space, gym.spaces.Box)
    assert env.action_space.shape == (2,)  # [direction, duration]    