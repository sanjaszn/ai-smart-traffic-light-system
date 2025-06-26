import pygame
import random
import time
import json
import os

# Define path to zone_counts.json
json_path = os.path.join(os.path.dirname(__file__), 'data', 'processed', 'zone_counts.json')

def read_zone_counts():
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {json_path} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {json_path}.")
        return {}

# Pygame Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Traffic Light Simulation")

# Colors
WHITE, BLACK, RED, GREEN, GREY = (255, 255, 255), (0, 0, 0), (200, 0, 0), (0, 200, 0), (120, 120, 120)
clock = pygame.time.Clock()

# Lane configuration
lanes = {
    'North': {'pos': (375, -50), 'dir': (0, 1)},
    'South': {'pos': (425, HEIGHT + 50), 'dir': (0, -1)},
    'East':  {'pos': (WIDTH + 50, 275), 'dir': (-1, 0)},
    'West':  {'pos': (-50, 325), 'dir': (1, 0)},
}
signal_positions = {
    'North': (360, 200),
    'South': (440, 400),
    'East': (500, 260),
    'West': (300, 340),
}

class Car:
    def __init__(self, direction):
        self.direction = direction
        self.x, self.y = lanes[direction]['pos']
        self.dir_x, self.dir_y = lanes[direction]['dir']
        self.stopped = False

    def move(self, green_direction):
        self.stopped = (self.direction != green_direction)
        if not self.stopped:
            self.x += self.dir_x * 2
            self.y += self.dir_y * 2

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, 20, 10))

# Simulation state
cars, spawn_timer = [], 0
spawn_interval = 60
green_duration = 5
last_switch_time = time.time()
green_direction = 'South'
zone_values = {'South': 0, 'East': 0, 'North': 0, 'West': 0}
last_zone_read_time = 0
zone_refresh_interval = 1  # seconds

running = True
while running:
    screen.fill(GREY)
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if current_time - last_zone_read_time > zone_refresh_interval:
        zone_counts = read_zone_counts()
        zone_values = {
            'South': zone_counts.get("Zone A", 0),
            'East':  zone_counts.get("Zone B", 0),
            'North': zone_counts.get("Zone C", 0),
            'West':  0  # Not used; included for structure
        }
        last_zone_read_time = current_time
        print("Updated zone counts:", zone_values)

    if current_time - last_switch_time > green_duration:
        new_green = max(zone_values, key=zone_values.get)
        if new_green != green_direction:
            green_direction = new_green
            print(f"Green light switched to: {green_direction}")
        last_switch_time = current_time

    spawn_timer += 1
    if spawn_timer >= spawn_interval:
        spawn_timer = 0
        cars.append(Car(random.choice(['North', 'South', 'East', 'West'])))

    for car in cars:
        car.move(green_direction)
        car.draw(screen)

    for direction, pos in signal_positions.items():
        pygame.draw.circle(screen, GREEN if direction == green_direction else RED, pos, 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
