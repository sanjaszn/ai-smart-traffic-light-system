#!/usr/bin/env python3
"""Enhanced Traffic Light Simulation Engine with RL Integration"""
import pygame
import time
import random
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from threading import Lock

# Enhanced Configuration with timing and vehicle parameters
CONFIG = {
    'WINDOW': (800, 600),
    'COLORS': {
        'WHITE': (255, 255, 255),
        'BLACK': (0, 0, 0),
        'RED': (255, 0, 0),
        'GREEN': (0, 255, 0),
        'GREY': (100, 100, 100),
        'YELLOW': (255, 255, 0),
        'LANE_COLOR': (200, 200, 200)
    },
    'LANES': {
        'North': {'pos': (375, -50), 'dir': (0, 1)},
        'South': {'pos': (425, 650), 'dir': (0, -1)},
        'East': {'pos': (850, 275), 'dir': (-1, 0)},
        'West': {'pos': (-50, 325), 'dir': (1, 0)}
    },
    'SIGNAL_POSITIONS': {
        'North': (360, 200),
        'South': (440, 400),
        'East': (500, 260),
        'West': (300, 340)
    },
    'TIMING': {
        'MIN_GREEN_DURATION': 2,  # Reduced from 3 to 2 seconds
        'MAX_GREEN_DURATION': 8,  # Reduced from 10 to 8 seconds
        'YELLOW_DURATION': 1,
        'SPAWN_INTERVAL': 0.5,
        'ZONE_REFRESH': 1.0
    },
    'VEHICLE': {
        'WIDTH': 30,
        'HEIGHT': 15,
        'SPEED': 3
    }
}

class Car:
    """Enhanced vehicle class with better visualization and performance"""
    
    def __init__(self, direction: str):
        self.direction = direction
        self.x, self.y = CONFIG['LANES'][direction]['pos']
        self.dir_x, self.dir_y = CONFIG['LANES'][direction]['dir']
        self.stopped = False
        self.width = CONFIG['VEHICLE']['WIDTH']
        self.height = CONFIG['VEHICLE']['HEIGHT']
        self.speed = CONFIG['VEHICLE']['SPEED']
        # Random color for each car
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    def move(self, green_direction: str):
        """Move car based on current traffic light - O(1) operation"""
        approaching = (
            (self.direction == 'North' and self.y < 250) or
            (self.direction == 'South' and self.y > 350) or
            (self.direction == 'East' and self.x > 450) or
            (self.direction == 'West' and self.x < 350)
        )
        
        self.stopped = approaching and (self.direction != green_direction)
        if not self.stopped:
            self.x += self.dir_x * self.speed
            self.y += self.dir_y * self.speed

    def draw(self, screen):
        """Draw car with enhanced visualization"""
        if self.stopped:
            pygame.draw.rect(screen, CONFIG['COLORS']['RED'], 
                           (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, self.color,
                           (self.x, self.y, self.width, self.height))
        # Add windshield for better visual appeal
        pygame.draw.rect(screen, CONFIG['COLORS']['BLACK'],
                       (self.x + 5, self.y + 3, self.width - 10, 3))

class TrafficSimulation:
    """Enhanced traffic light simulation with RL integration capabilities"""
    
    def __init__(self, data_file: str = "data/processed/zone_counts.json"):
        self.data_file = Path(data_file)
        self.zone_values = {'South': 0, 'East': 0, 'North': 0, 'West': 0}
        self.last_modified = 0
        self.auto_update = True
        
        # Thread safety for data access
        self._data_lock = Lock()
        
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode(CONFIG['WINDOW'])
        pygame.display.set_caption("AI Traffic Light Simulation")
        self.clock = pygame.time.Clock()
        
        # Simulation state
        self.cars: List[Car] = []
        self.green_direction = 'South'
        self.next_green_direction = None
        self.last_switch_time = time.time()
        self.yellow_light_start = 0
        self.running = True
        self.car_spawn_rates = {'South': 0, 'East': 0, 'North': 0, 'West': 0}
        self.last_spawn_time = time.time()
        
        # RL integration
        self.rl_controller = None
        self.rl_mode = False

    def set_manual_mode(self):
        """Disable automatic JSON polling"""
        self.auto_update = False

    def set_rl_mode(self, rl_controller):
        """Enable RL agent control using RL Controller"""
        self.rl_controller = rl_controller
        self.rl_mode = True
        print("🤖 RL mode enabled - using trained agent for traffic control")

    def check_for_updates(self):
        """Check for zone count updates - thread-safe"""
        if not self.auto_update:
            return False
            
        try:
            with self._data_lock:
                current_modified = self.data_file.stat().st_mtime
                if current_modified > self.last_modified:
                    self.last_modified = current_modified
                    counts = json.loads(self.data_file.read_text())
                    self.update_zone_counts(counts)
                    print(f"File updated, new counts: {counts}")
                    return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading zone counts: {e}")
        return False

    def update_zone_counts(self, zone_counts: Dict[str, int]):
        """Update simulation with new zone counts"""
        self.zone_values = {
            'South': zone_counts.get("Zone A", 0),
            'East': zone_counts.get("Zone B", 0),
            'North': zone_counts.get("Zone C", 0),
            'West': zone_counts.get("Zone D", 0)
        }
        
        # Normalize spawn rates - O(1) operation
        total = sum(self.zone_values.values()) or 1
        for direction in self.zone_values:
            self.car_spawn_rates[direction] = self.zone_values[direction] / total
        
        # Debug output
        print(f"Updated zone counts: {self.zone_values}")

    def get_state_for_rl(self) -> Dict[str, Any]:
        """Get current state for RL agent - O(1) operation"""
        return {
            'South': self.zone_values['South'],
            'East': self.zone_values['East'], 
            'North': self.zone_values['North'],
            'West': self.zone_values['West'],
            'current_phase': self._direction_to_phase(self.green_direction),
            'elapsed_time': time.time() - self.last_switch_time
        }

    def _direction_to_phase(self, direction: str) -> int:
        """Convert direction string to phase number - O(1) lookup"""
        return {'North': 0, 'East': 1, 'South': 2, 'West': 3}[direction]

    def _phase_to_direction(self, phase: int) -> str:
        """Convert phase number to direction string - O(1) lookup"""
        return ['North', 'East', 'South', 'West'][phase]

    def update_traffic_lights(self):
        """Update traffic lights based on current state or RL agent"""
        current_time = time.time()
        time_since_switch = current_time - self.last_switch_time
        
        # Handle yellow light transition
        if self.next_green_direction:
            if current_time - self.yellow_light_start >= CONFIG['TIMING']['YELLOW_DURATION']:
                self.green_direction = self.next_green_direction
                self.next_green_direction = None
                self.last_switch_time = current_time
            return
        
        # RL agent decision
        if self.rl_mode and self.rl_controller:
            try:
                state = self.get_state_for_rl()
                direction, duration = self.rl_controller.get_action(state)
                
                if direction != self.green_direction:
                    self.next_green_direction = direction
                    self.yellow_light_start = current_time
                    print(f"🧠 RL Decision: {direction} for {duration:.1f}s")
                return
            except Exception as e:
                print(f"RL agent error: {e}, falling back to rule-based")
                self.rl_mode = False
        
        # Rule-based logic (fallback) - O(1) operation
        max_count = max(self.zone_values.values())
        min_duration = CONFIG['TIMING']['MIN_GREEN_DURATION']
        max_duration = CONFIG['TIMING']['MAX_GREEN_DURATION']
        
        # More responsive duration calculation
        desired_duration = min(max_duration, min_duration + max_count * 0.3)  # Reduced multiplier
            
        if time_since_switch > desired_duration:
            # Find the direction with the highest traffic count
            current_count = self.zone_values[self.green_direction]
            best_direction = max(self.zone_values, key=self.zone_values.get)
            best_count = self.zone_values[best_direction]
            
            # Switch if there's a better direction (higher count)
            # or if current direction has no traffic and another has traffic
            if (best_direction != self.green_direction and 
                (best_count > current_count or (current_count == 0 and best_count > 0))):
                self.next_green_direction = best_direction
                self.yellow_light_start = current_time
                print(f"🔄 Switching from {self.green_direction} ({current_count}) to {best_direction} ({best_count})")

    def spawn_cars(self):
        """Spawn cars based on zone counts - optimized algorithm"""
        current_time = time.time()
        if current_time - self.last_spawn_time < CONFIG['TIMING']['SPAWN_INTERVAL']:
            return
            
        # Use zone counts directly for spawning
        total_traffic = sum(self.zone_values.values())
        if total_traffic == 0:
            return
            
        # Optimized spawning logic - O(1) operation
        for direction, count in self.zone_values.items():
            if count > 0:
                # Spawn probability based on count
                spawn_prob = min(0.8, count / (total_traffic + 1))
                if random.random() < spawn_prob:
                    self.cars.append(Car(direction))
                    self.last_spawn_time = current_time
                    print(f"Spawned car in {direction} direction (count: {count})")
                    break  # Only spawn one car per update to avoid flooding

    def render(self):
        """Enhanced rendering with lane markings and better visuals"""
        self.screen.fill(CONFIG['COLORS']['GREY'])
        
        # Draw lane markings
        for lane in CONFIG['LANES'].values():
            start_pos = lane['pos']
            if lane['dir'][0] == 0:  # Vertical lanes
                pygame.draw.line(self.screen, CONFIG['COLORS']['LANE_COLOR'], 
                               (start_pos[0], 0), (start_pos[0], CONFIG['WINDOW'][1]), 2)
            else:  # Horizontal lanes
                pygame.draw.line(self.screen, CONFIG['COLORS']['LANE_COLOR'],
                               (0, start_pos[1]), (CONFIG['WINDOW'][0], start_pos[1]), 2)
        
        # Draw traffic lights
        current_time = time.time()
        for direction, pos in CONFIG['SIGNAL_POSITIONS'].items():
            if direction == self.green_direction:
                color = CONFIG['COLORS']['GREEN']
            elif self.next_green_direction and direction in [self.green_direction, self.next_green_direction]:
                if (current_time - self.yellow_light_start) % 0.5 < 0.25:
                    color = CONFIG['COLORS']['YELLOW']
                else:
                    color = CONFIG['COLORS']['BLACK']
            else:
                color = CONFIG['COLORS']['RED']
            
            pygame.draw.circle(self.screen, color, pos, 10)
        
        # Handle cars
        self.spawn_cars()
        for car in self.cars[:]:
            car.move(self.green_direction)
            car.draw(self.screen)
            if self._is_off_screen(car):
                self.cars.remove(car)
        
        # Display zone counts and mode
        font = pygame.font.SysFont(None, 24)
        y_offset = 20
        
        # Mode indicator
        mode_text = "RL Mode" if self.rl_mode else "Rule-Based"
        mode_color = CONFIG['COLORS']['GREEN'] if self.rl_mode else CONFIG['COLORS']['YELLOW']
        text = font.render(f"Mode: {mode_text}", True, mode_color)
        self.screen.blit(text, (10, y_offset))
        y_offset += 25
        
        # Zone counts
        for zone, count in self.zone_values.items():
            color = CONFIG['COLORS']['GREEN'] if zone == self.green_direction else CONFIG['COLORS']['BLACK']
            text = font.render(f"{zone}: {count}", True, color)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()

    def _is_off_screen(self, car) -> bool:
        """Check if car is outside visible area - O(1) operation"""
        return (car.x < -100 or car.x > CONFIG['WINDOW'][0] + 100 or 
                car.y < -100 or car.y > CONFIG['WINDOW'][1] + 100)

    def run(self):
        """Main simulation loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            self.check_for_updates()
            self.update_traffic_lights()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()

    def quit(self):
        """Clean shutdown"""
        self.running = False
        pygame.quit()


if __name__ == "__main__":
    sim = TrafficSimulation()
    sim.run()