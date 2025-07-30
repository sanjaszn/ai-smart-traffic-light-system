#!/usr/bin/env python3
"""Traffic Light Simulation Module"""
import pygame
import json
import random
import time
from pathlib import Path
from typing import Dict, Optional
from threading import Lock

# Configuration
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
    }
}

class Car:
    def __init__(self, direction: str):
        self.direction = direction
        self.x, self.y = CONFIG['LANES'][direction]['pos']
        self.dir_x, self.dir_y = CONFIG['LANES'][direction]['dir']
        self.stopped = False
        self.width = 30
        self.height = 15
        self.speed = 3
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255)
        )

    def move(self, green_direction: str):
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
        if self.stopped:
            pygame.draw.rect(screen, CONFIG['COLORS']['RED'], 
                           (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, self.color,
                           (self.x, self.y, self.width, self.height))
        # Add windshield
        pygame.draw.rect(screen, CONFIG['COLORS']['BLACK'],
                       (self.x + 5, self.y + 3, self.width - 10, 3))

class TrafficSimulation:
    def __init__(self, data_file: str = "data/processed/zone_counts.json"):
        self.data_file = Path(data_file)
        self.zone_values = {'South': 0, 'East': 0, 'North': 0, 'West': 0}
        self.last_modified = 0
        
        pygame.init()
        self.screen = pygame.display.set_mode(CONFIG['WINDOW'])
        pygame.display.set_caption("AI Traffic Light Simulation")
        self.clock = pygame.time.Clock()
        
        self.cars = []
        self.green_direction = 'South'
        self.next_green_direction = None
        self.last_switch_time = time.time()
        self.yellow_light_start = 0
        self.running = True
        self.car_spawn_rates = {'South': 0, 'East': 0, 'North': 0, 'West': 0}
        self.last_spawn_time = time.time()
        self.auto_update = True

    def set_manual_mode(self):
        self.auto_update = False

    def check_for_updates(self):
        if not self.auto_update:
            return False
            
        try:
            current_modified = self.data_file.stat().st_mtime
            if current_modified > self.last_modified:
                self.last_modified = current_modified
                counts = json.loads(self.data_file.read_text())
                self.update_zone_counts(counts)
                return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading zone counts: {e}")
        return False

    def update_zone_counts(self, zone_counts: Dict[str, int]):
        self.zone_values = {
            'South': zone_counts.get("Zone A", 0),
            'East': zone_counts.get("Zone B", 0),
            'North': zone_counts.get("Zone C", 0),
            'West': zone_counts.get("Zone D", 0)
        }
        total = sum(self.zone_values.values()) or 1
        for direction in self.zone_values:
            self.car_spawn_rates[direction] = self.zone_values[direction] / total

    def update_traffic_lights(self):
        current_time = time.time()
        time_since_switch = current_time - self.last_switch_time
        
        if self.next_green_direction:
            if current_time - self.yellow_light_start >= 1.0:
                self.green_direction = self.next_green_direction
                self.next_green_direction = None
                self.last_switch_time = current_time
            return
        
        max_count = max(self.zone_values.values())
        desired_duration = min(10, 3 + max_count * 0.5)
            
        if time_since_switch > desired_duration:
            candidates = {k: v for k, v in self.zone_values.items() 
                        if k != self.green_direction and v > 0}
            if candidates:
                new_green = max(candidates, key=candidates.get)
                if self.zone_values[new_green] > self.zone_values[self.green_direction]:
                    self.next_green_direction = new_green
                    self.yellow_light_start = current_time

    def spawn_cars(self):
        current_time = time.time()
        if current_time - self.last_spawn_time < 0.5:
            return
            
        total_traffic = sum(self.zone_values.values())
        if total_traffic == 0:
            return
            
        for direction in self.zone_values:
            spawn_prob = min(0.9, self.zone_values[direction] / (total_traffic + 1))
            if random.random() < spawn_prob * 0.8:
                self.cars.append(Car(direction))
                self.last_spawn_time = current_time

    def render(self):
        self.screen.fill(CONFIG['COLORS']['GREY'])
        
        # Draw lane markings
        for lane in CONFIG['LANES'].values():
            start_pos = lane['pos']
            if lane['dir'][0] == 0:
                pygame.draw.line(self.screen, CONFIG['COLORS']['LANE_COLOR'], 
                               (start_pos[0], 0), (start_pos[0], CONFIG['WINDOW'][1]), 2)
            else:
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
        
        # Display counts
        font = pygame.font.SysFont(None, 24)
        y_offset = 20
        for zone, count in self.zone_values.items():
            color = CONFIG['COLORS']['GREEN'] if zone == self.green_direction else CONFIG['COLORS']['BLACK']
            text = font.render(f"{zone}: {count}", True, color)
            self.screen.blit(text, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()

    def _is_off_screen(self, car) -> bool:
        return (car.x < -100 or car.x > CONFIG['WINDOW'][0] + 100 or 
                car.y < -100 or car.y > CONFIG['WINDOW'][1] + 100)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.check_for_updates()
            self.update_traffic_lights()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()

    def quit(self):
        self.running = False
        pygame.quit() 