#!/usr/bin/env python3
"""
Test runner for DarkVidCreator project.
Runs all unit tests and integration tests.
"""

import unittest
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Run all tests in the tests directory."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run a specific test module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{test_module}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

def main():
    """Main entry point for test runner."""
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        print(f"Running tests for module: {test_module}")
        exit_code = run_specific_test(test_module)
    else:
        # Run all tests
        print("Running all tests...")
        exit_code = run_tests()
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()