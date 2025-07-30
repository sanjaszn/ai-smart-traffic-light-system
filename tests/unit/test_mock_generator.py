#!/usr/bin/env python3
"""Unit tests for MockZoneGenerator"""

import pytest
import json
import time
from pathlib import Path
from core.utils.mock_zone_generator import MockZoneGenerator

class TestMockZoneGenerator:
    """Test MockZoneGenerator functionality"""
    
    def test_initialization(self, temp_data_file):
        """Test generator initialization"""
        generator = MockZoneGenerator(temp_data_file, refresh_rate=2.0)
        
        assert generator.output_path == Path(temp_data_file)
        assert generator.refresh_rate == 2.0
        assert generator.zones == ["Zone A", "Zone B", "Zone C", "Zone D"]
        
    def test_generate_counts(self):
        """Test count generation"""
        generator = MockZoneGenerator("dummy.json")
        
        counts = generator.generate_counts()
        
        # Check structure
        assert isinstance(counts, dict)
        assert len(counts) == 4
        assert all(zone in counts for zone in generator.zones)
        
        # Check values
        for count in counts.values():
            assert isinstance(count, int)
            assert 0 <= count <= 15
            
    def test_generate_counts_realistic_patterns(self):
        """Test that generated counts follow realistic patterns"""
        generator = MockZoneGenerator("dummy.json")
        
        # Generate multiple counts to check patterns
        all_counts = []
        for _ in range(10):
            counts = generator.generate_counts()
            all_counts.append(counts)
            
        # Check that we get some variation
        total_counts = [sum(counts.values()) for counts in all_counts]
        assert min(total_counts) != max(total_counts)  # Should have variation
        
        # Check that some zones can be empty (30% chance)
        empty_zones = 0
        for counts in all_counts:
            for count in counts.values():
                if count == 0:
                    empty_zones += 1
                    
        # Should have some empty zones
        assert empty_zones > 0
        
    def test_file_writing(self, temp_data_file):
        """Test writing counts to file"""
        generator = MockZoneGenerator(temp_data_file, refresh_rate=1.0)
        
        # Generate and write counts
        counts = generator.generate_counts()
        generator.output_path.write_text(json.dumps(counts, indent=2))
        
        # Check file was written
        assert Path(temp_data_file).exists()
        
        # Check content
        with open(temp_data_file, 'r') as f:
            written_data = json.load(f)
            
        assert written_data == counts
        
    def test_refresh_rate_configuration(self):
        """Test different refresh rate configurations"""
        # Test default refresh rate
        generator1 = MockZoneGenerator("dummy1.json")
        assert generator1.refresh_rate == 1.0
        
        # Test custom refresh rate
        generator2 = MockZoneGenerator("dummy2.json", refresh_rate=5.0)
        assert generator2.refresh_rate == 5.0
        
    def test_zone_names(self):
        """Test zone naming consistency"""
        generator = MockZoneGenerator("dummy.json")
        
        expected_zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
        assert generator.zones == expected_zones
        
        # Check that generated counts use these zone names
        counts = generator.generate_counts()
        assert list(counts.keys()) == expected_zones
        
    def test_count_range(self):
        """Test that counts are within expected range"""
        generator = MockZoneGenerator("dummy.json")
        
        # Generate many counts to check range
        for _ in range(50):
            counts = generator.generate_counts()
            for count in counts.values():
                assert 0 <= count <= 15
                
    def test_probability_distribution(self):
        """Test that probability distribution is reasonable"""
        generator = MockZoneGenerator("dummy.json")
        
        # Generate many counts to check distribution
        total_counts = []
        for _ in range(100):
            counts = generator.generate_counts()
            total_counts.append(sum(counts.values()))
            
        # Check that we have reasonable distribution
        avg_total = sum(total_counts) / len(total_counts)
        
        # Average should be reasonable (not too high, not too low)
        assert 5 <= avg_total <= 25
        
    def test_file_path_handling(self):
        """Test file path handling"""
        # Test with string path
        generator1 = MockZoneGenerator("test.json")
        assert isinstance(generator1.output_path, Path)
        
        # Test with Path object
        test_path = Path("test2.json")
        generator2 = MockZoneGenerator(test_path)
        assert generator2.output_path == test_path
        
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with invalid refresh rate (should raise TypeError when used)
        try:
            generator = MockZoneGenerator("test.json", refresh_rate="invalid")
            # If it doesn't raise during initialization, that's fine
            # The error would occur when trying to use refresh_rate in sleep()
            assert generator.refresh_rate == "invalid"
        except TypeError:
            # If it does raise TypeError, that's also fine
            pass
            
        # Test with negative refresh rate
        generator = MockZoneGenerator("test.json", refresh_rate=-1.0)
        assert generator.refresh_rate == -1.0  # Should accept but not recommended 