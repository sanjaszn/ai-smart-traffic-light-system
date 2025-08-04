#!/usr/bin/env python3
"""AI Traffic Light System - Main Application with RL Integration"""
import sys
import os
import time
import pygame
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.simulation.engine import TrafficSimulation
from core.utils.mock_zone_generator import MockZoneGenerator
from core.control.rl.controller import create_rl_controller
from core.utils.logger import get_logger

logger = get_logger(__name__)

# Configuration
DATA_FILE = "data/processed/zone_counts.json"
UPDATE_INTERVAL = 1.0

def main():
    """Main application entry point with RL integration"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Traffic Light System")
    parser.add_argument("--rl", action="store_true", help="Enable RL mode")
    parser.add_argument("--model", type=str, help="Path to trained RL model")
    parser.add_argument("--random", action="store_true", help="Use random actions (for testing)")
    args = parser.parse_args()
    
    try:
        logger.info("Starting AI Traffic Light System")
        
        # Initialize RL controller if requested
        rl_controller = None
        if args.rl or args.model or args.random:
            if args.model:
                logger.info(f"Loading RL model from: {args.model}")
                rl_controller = create_rl_controller(model_path=args.model)
            elif args.random:
                logger.info("Using random actions for testing")
                rl_controller = create_rl_controller()  # No model = random actions
            else:
                logger.info("RL mode enabled but no model specified - using random actions")
                rl_controller = create_rl_controller()
        
        # Initialize mock data generator with slower updates
        mock_generator = MockZoneGenerator(DATA_FILE, 20.0)  # Update every 20 seconds
        
        # Ensure data directory exists
        Path(DATA_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with some traffic data
        initial_data = {"Zone A": 5, "Zone B": 3, "Zone C": 7, "Zone D": 2}
        mock_generator.output_path.write_text(json.dumps(initial_data, indent=2))
        
        # Start mock data generation in background
        import threading
        mock_thread = threading.Thread(target=mock_generator.run, daemon=True)
        mock_thread.start()
        
        # Initialize simulation
        sim = TrafficSimulation(DATA_FILE)
        # Keep auto_update enabled for dynamic updates
        sim.auto_update = True
        
        # Enable RL mode if controller is available
        if rl_controller:
            sim.set_rl_mode(rl_controller)
            logger.info("RL mode enabled - traffic lights controlled by AI agent")
        else:
            logger.info("Rule-based mode - traffic lights controlled by traditional logic")
        
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
                    elif event.key == pygame.K_r and rl_controller:
                        # Toggle RL mode with 'R' key
                        sim.rl_mode = not sim.rl_mode
                        mode = "RL" if sim.rl_mode else "Rule-based"
                        logger.info(f"Switched to {mode} mode")
                    elif event.key == pygame.K_s and rl_controller:
                        # Show RL stats with 'S' key
                        stats = rl_controller.get_stats()
                        logger.info(f"RL Stats: {stats}")
            
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