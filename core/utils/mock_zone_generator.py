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
        # More balanced base counts to eliminate bias
        self.base_counts = {"Zone A": 3, "Zone B": 3, "Zone C": 3, "Zone D": 3}
        self.stability_counter = 0  # Counter to maintain stability
        
    def generate_counts(self) -> Dict[str, int]:
        """Generates realistic traffic patterns with more stability and fairness"""
        counts = {}
        
        # Only change traffic patterns every few iterations for stability
        if self.stability_counter % 3 == 0:  # Change every 3 iterations
            for zone in self.zones:
                base = self.base_counts[zone]
                # Smaller variations for more stability
                variation = random.randint(-1, 2)
                count = max(0, base + variation)
                
                # Rare traffic spikes (5% chance) - apply to any zone equally
                if random.random() < 0.05:
                    count = random.randint(8, 12)
                
                counts[zone] = count
                
                # Gradual base count changes - keep them balanced
                change = random.randint(-1, 1)
                self.base_counts[zone] = max(2, min(6, base + change))  # Keep between 2-6
        else:
            # Keep the same pattern for stability
            for zone in self.zones:
                base = self.base_counts[zone]
                # Very small variations
                variation = random.randint(-1, 1)
                count = max(0, base + variation)
                counts[zone] = count
        
        self.stability_counter += 1
        return counts

    def run(self):
        """Continuously writes mock data to JSON"""
        print(f"🚗 Starting mock traffic generator (updates every {self.refresh_rate}s)")
        while True:
            counts = self.generate_counts()
            self.output_path.write_text(json.dumps(counts, indent=2))
            print(f"📊 Updated traffic: {counts}")
            time.sleep(self.refresh_rate)

if __name__ == "__main__":
    generator = MockZoneGenerator(
        output_path="data/processed/zone_counts.json",
        refresh_rate=20.0  # Update every 20 seconds
    )
    generator.run()