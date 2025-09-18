#!/usr/bin/env python3
"""
Simple test runner for the navigator_dagster project.
Run this script to execute all tests.
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests using pytest."""
    # Change to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    # Run pytest with verbose output
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]

    print("Running tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("All tests passed! ✅")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"Tests failed with exit code {e.returncode} ❌")
        return e.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with:")
        print("pip install pytest pytest-mock")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
