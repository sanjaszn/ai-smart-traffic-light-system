import random
import json
import time
from pathlib import Path
from typing import Dict

class MockZoneGenerator:
    def __init__(self, output_path: str, refresh_rate: float = 1.0):
        self.output_path = Path(output_path)
        self.refresh_rate = refresh_rate
        self.zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
        
    def generate_counts(self) -> Dict[str, int]:
        """Generates realistic traffic patterns"""
        return {
            zone: random.randint(0, 15) 
            if random.random() > 0.3  # 70% chance of activity
            else 0
            for zone in self.zones
        }

    def run(self):
        """Continuously writes mock data to JSON"""
        while True:
            counts = self.generate_counts()
            self.output_path.write_text(json.dumps(counts, indent=2))
            time.sleep(self.refresh_rate)

if __name__ == "__main__":
    generator = MockZoneGenerator(
        output_path="data/processed/zone_counts.json",
        refresh_rate=30.0  # Update twice per second
    )
    generator.run()