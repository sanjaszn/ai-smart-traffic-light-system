#!/usr/bin/env python3
"""AI Traffic Light System - Main Application (Simplified)"""
import sys
import os
import time
import pygame
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.simulation.engine import TrafficSimulation
from core.utils.mock_zone_generator import MockZoneGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
DATA_FILE = "data/processed/zone_counts.json"
UPDATE_INTERVAL = 1.0

def main():
    """Main application entry point"""
    try:
        logger.info("Starting AI Traffic Light System")
        
        # Initialize mock data generator
        mock_generator = MockZoneGenerator(DATA_FILE, 20.0)  # Update every 20 seconds
        
        # Ensure data directory exists
        Path(DATA_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with empty counts
        mock_generator.output_path.write_text('{"Zone A": 0, "Zone B": 0, "Zone C": 0, "Zone D": 0}')
        
        # Start mock data generation in background
        import threading
        mock_thread = threading.Thread(target=mock_generator.run, daemon=True)
        mock_thread.start()
        
        # Initialize simulation
        sim = TrafficSimulation(DATA_FILE)
        sim.set_manual_mode()  # Manual mode for controlled updates
        
        # Main application loop
        last_update = 0
        running = True
        
        while running:
            current_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update simulation with current data
            if current_time - last_update >= UPDATE_INTERVAL:
                sim.check_for_updates()
                last_update = current_time
            
            # Update and render simulation
            sim.update_traffic_lights()
            sim.render()
            
            # Control frame rate
            sim.clock.tick(60)
        
        logger.info("Shutting down AI Traffic Light System")
        sim.quit()
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        pygame.quit()

if __name__ == "__main__":
    main()