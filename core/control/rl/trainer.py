import os
import time
import numpy as np
from datetime import datetime
from stable_baselines3.common.monitor import Monitor
from core.control.rl.agent import build_agent, TensorboardCallback
from core.control.rl.env import TrafficLightEnv

def train():
    # Setup directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = f"logs/ppo_{timestamp}"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create and wrap environment
    env = TrafficLightEnv()
    env = Monitor(env, log_dir)
    
    # Build agent
    agent = build_agent(env)
    
    # Training parameters
    total_steps = 1_000_000
    chunk_size = 100_000
    callbacks = [TensorboardCallback()]

    print("=== Training Started ===")
    print(f"Logging to: {log_dir}")
    
    for i in range(total_steps // chunk_size):
        agent.learn(
            total_timesteps=chunk_size,
            callback=callbacks,
            reset_num_timesteps=False,
            tb_log_name="ppo"
        )
        
        # Save checkpoint
        checkpoint_path = f"{log_dir}/ppo_{chunk_size*(i+1)}_steps"
        agent.save(checkpoint_path)
        print(f"Saved checkpoint: {checkpoint_path}")
        
        # Validation
        if (i + 1) % 2 == 0:  # Validate every 2 chunks
            validate(agent, env)

def validate(agent, env, n_episodes=5):
    """Enhanced validation with action statistics"""
    from core.control.rules.scheduler import RuleBasedScheduler
    
    rule_based = RuleBasedScheduler()
    rl_rewards = []
    rule_rewards = []
    action_stats = []

    print("\n=== Validation ===")
    
    for _ in range(n_episodes):
        # RL Agent Test
        obs, _ = env.reset()
        episode_reward = 0
        while True:
            action, _ = agent.predict(obs, deterministic=True)
            obs, reward, _, truncated, _ = env.step(action)
            
            action_stats.append(action)
            episode_reward += reward
            
            if truncated:
                break
        rl_rewards.append(episode_reward)

        # Rule-Based Test
        obs, _ = env.reset()
        episode_reward = 0
        while True:
            action = rule_based.predict(obs)
            obs, reward, _, truncated, _ = env.step(action)
            episode_reward += reward
            if truncated:
                break
        rule_rewards.append(episode_reward)

    # Action analysis
    actions = np.array(action_stats)
    print(f"\nAction Statistics (mean ± std):")
    print(f"Direction: {actions[:,0].mean():.2f} ± {actions[:,0].std():.2f}")
    print(f"Duration: {actions[:,1].mean():.2f} ± {actions[:,1].std():.2f}")

    # Reward comparison
    print("\nReward Comparison:")
    print(f"RL Agent: {np.mean(rl_rewards):.1f} (max: {np.max(rl_rewards):.1f})")
    print(f"Rule-Based: {np.mean(rule_rewards):.1f} (max: {np.max(rule_rewards):.1f})")

if __name__ == "__main__":
    train()