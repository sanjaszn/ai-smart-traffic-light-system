'''This script will:

Simulate time steps (like every 10 seconds).

Read traffic counts (we’ll mock this first).

Use traffic rules to choose green direction.

Print/log which light is green and for how long.'''

# === smart_controller.py ===
# Rule-based simulation of smart traffic light system
# Reads vehicle counts and decides green direction with dynamic duration

# Current: Rule-based system
# Roadmap: To be replaced with RL agent (Q-learning/DQN) in v2

import time
import random

# Step 1: Mock traffic data - this will be replaced by actual zone count JSON
def get_mock_vehicle_counts():
    """
    Returns mock vehicle count data for four directions.
    """
    return {
        'North': random.randint(5, 50),
        'East': random.randint(5, 50),
        'South': random.randint(5, 50),
        'West': random.randint(5, 50)
    }

# Step 2: Decision logic
def decide_green_light(vehicle_counts):
    """
    Returns the direction with the highest number of vehicles.
    """
    return max(vehicle_counts, key=vehicle_counts.get)

# Step 3: Main loop
def simulate_traffic_lights():
    """
    Simulates the smart traffic light controller in real-time.
    """
    while True:
        vehicle_counts = get_mock_vehicle_counts()
        green_direction = decide_green_light(vehicle_counts)
        
        green_duration = min(30, 10 + vehicle_counts[green_direction] // 2)

        print("\nTraffic counts:", vehicle_counts)
        print(f"🟢 Green light → {green_direction} for {green_duration} seconds")

        time.sleep(green_duration)

if __name__ == "__main__":
    simulate_traffic_lights()
