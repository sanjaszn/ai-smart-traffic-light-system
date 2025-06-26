'''A Pygame-based visual simulation of a 4-way smart traffic light system that:

Displays an intersection (North, East, South, West) with real-time traffic counts.

Prioritizes the busiest direction (most vehicles) for the green light.

Sets green time:
Minimum: 15 sec
Maximum: 30 sec

Otherwise: half the vehicle count (// 2)

Visuals:

Highlights active direction with a green bar.

Shows live vehicle counts on-screen and in the console.

Runs indefinitely until manually closed.'''

import pygame
import sys
import time
import random

# === CONFIG ===
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
FPS = 60
FONT_SIZE = 24
DIRECTIONS = ["North", "East", "South", "West"]

# Traffic light timing boundaries
MIN_GREEN_TIME = 15
MAX_GREEN_TIME = 30

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
GRAY = (180, 180, 180)

# Setup
pygame.init()
win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Smart Traffic Light Simulation")
font = pygame.font.SysFont("Arial", FONT_SIZE)
clock = pygame.time.Clock()

# Position mappings for highlighting
def get_direction_rect(direction):
    padding = 200
    thickness = 100
    if direction == "North":
        return pygame.Rect(WINDOW_WIDTH//2 - thickness//2, 0, thickness, padding)
    elif direction == "South":
        return pygame.Rect(WINDOW_WIDTH//2 - thickness//2, WINDOW_HEIGHT - padding, thickness, padding)
    elif direction == "East":
        return pygame.Rect(WINDOW_WIDTH - padding, WINDOW_HEIGHT//2 - thickness//2, padding, thickness)
    elif direction == "West":
        return pygame.Rect(0, WINDOW_HEIGHT//2 - thickness//2, padding, thickness)

# Simulate traffic counts
def simulate_traffic_counts():
    return {
        "North": random.randint(5, 50),
        "East": random.randint(5, 50),
        "South": random.randint(5, 50),
        "West": random.randint(5, 50),
    }

# Decision logic (replicates smart_controller.py)
def choose_green_light_direction(traffic_counts):
    return max(traffic_counts, key=traffic_counts.get)

def get_green_duration(vehicle_count):
    return max(MIN_GREEN_TIME, min(MAX_GREEN_TIME, vehicle_count // 2))

# Drawing functions
def draw_intersection():
    win.fill(GRAY)
    pygame.draw.line(win, BLACK, (0, WINDOW_HEIGHT//2), (WINDOW_WIDTH, WINDOW_HEIGHT//2), 5)
    pygame.draw.line(win, BLACK, (WINDOW_WIDTH//2, 0), (WINDOW_WIDTH//2, WINDOW_HEIGHT), 5)

def draw_direction_labels():
    positions = {
        "North": (WINDOW_WIDTH//2, 50),
        "South": (WINDOW_WIDTH//2, WINDOW_HEIGHT - 50),
        "East": (WINDOW_WIDTH - 50, WINDOW_HEIGHT//2),
        "West": (50, WINDOW_HEIGHT//2),
    }
    for direction, pos in positions.items():
        label = font.render(direction, True, BLACK)
        rect = label.get_rect(center=pos)
        win.blit(label, rect)

def draw_green_highlight(direction):
    rect = get_direction_rect(direction)
    pygame.draw.rect(win, GREEN, rect)

def draw_traffic_counts(traffic_counts):
    y_offset = 20
    for i, (dir, count) in enumerate(traffic_counts.items()):
        label = font.render(f"{dir}: {count} vehicles", True, BLACK)
        win.blit(label, (20, y_offset + i * (FONT_SIZE + 5)))

# === MAIN LOOP ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Simulate step
    traffic_counts = simulate_traffic_counts()
    green_dir = choose_green_light_direction(traffic_counts)
    green_time = get_green_duration(traffic_counts[green_dir])

    print(f"Traffic counts: {traffic_counts}")
    print(f"\U0001F7E2 Green light → {green_dir} for {green_time} seconds\n")

    # Draw
    draw_intersection()
    draw_green_highlight(green_dir)
    draw_direction_labels()
    draw_traffic_counts(traffic_counts)
    pygame.display.update()

    # Wait for duration of green light
    start_time = time.time()
    while time.time() - start_time < green_time:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        draw_intersection()
        draw_green_highlight(green_dir)
        draw_direction_labels()
        draw_traffic_counts(traffic_counts)
        pygame.display.update()
