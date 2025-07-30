#!/usr/bin/env python3
"""Test runner for AI Traffic Light System"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short",
        "--durations=10"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/integration/", 
        "-v", 
        "--tb=short",
        "--durations=10"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def run_all_tests():
    """Run all tests"""
    print("\n🚦 Running All Tests...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--durations=10"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def run_coverage():
    """Run tests with coverage"""
    print("\n📊 Running Tests with Coverage...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "--cov=core",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def run_specific_test(test_path):
    """Run a specific test file"""
    print(f"\n🎯 Running Specific Test: {test_path}")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        test_path, 
        "-v", 
        "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
        
    return result.returncode == 0

def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔍 Checking Test Environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print("✅ pytest is installed")
    except ImportError:
        print("❌ pytest is not installed. Install with: pip install pytest")
        return False
    
    # Check if test directories exist
    test_dirs = ["tests", "tests/unit", "tests/integration"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir} exists")
        else:
            print(f"❌ {test_dir} does not exist")
            return False
    
    # Check if core modules can be imported
    try:
        from core.evaluation import TrafficMetrics
        from core.control.rules.scheduler import RuleBasedScheduler
        from core.utils.mock_zone_generator import MockZoneGenerator
        print("✅ Core modules can be imported")
    except ImportError as e:
        print(f"❌ Core modules cannot be imported: {e}")
        return False
    
    print("✅ Test environment is ready!")
    return True

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='AI Traffic Light System Test Runner')
    parser.add_argument('--type', choices=['unit', 'integration', 'all', 'coverage'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--test', type=str, help='Run specific test file')
    parser.add_argument('--check', action='store_true', help='Check test environment')
    
    args = parser.parse_args()
    
    print("🚦 AI Traffic Light System - Test Runner")
    print("=" * 60)
    
    # Check environment if requested
    if args.check:
        if not check_test_environment():
            return 1
        return 0
    
    # Run specific test if provided
    if args.test:
        success = run_specific_test(args.test)
    else:
        # Run tests based on type
        if args.type == 'unit':
            success = run_unit_tests()
        elif args.type == 'integration':
            success = run_integration_tests()
        elif args.type == 'coverage':
            success = run_coverage()
        else:  # all
            success = run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 