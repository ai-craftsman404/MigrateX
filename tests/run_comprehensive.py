"""
Comprehensive test runner with coverage enforcement
"""

import pytest
import sys
from pathlib import Path


def main():
    """Run comprehensive test suite with coverage enforcement."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Run pytest with comprehensive options
    pytest_args = [
        "tests/",
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--strict-markers",  # Strict marker usage
        "--strict-config",  # Strict config
        "--cov=migratex",  # Coverage for migratex
        "--cov-report=term-missing",  # Show missing lines
        "--cov-report=html",  # HTML report
        "--cov-report=xml",  # XML report for CI
        "--cov-fail-under=90",  # Fail if coverage < 90%
        "-m", "not slow",  # Skip slow tests by default
    ]
    
    # Add markers for different test types
    if "--unit-only" in sys.argv:
        pytest_args.extend(["-m", "unit"])
    elif "--integration-only" in sys.argv:
        pytest_args.extend(["-m", "integration"])
    elif "--e2e-only" in sys.argv:
        pytest_args.extend(["-m", "e2e"])
    elif "--edge-cases-only" in sys.argv:
        pytest_args.extend(["-m", "edge_case"])
    elif "--outliers-only" in sys.argv:
        pytest_args.extend(["-m", "outlier"])
    elif "--performance-only" in sys.argv:
        pytest_args.extend(["-m", "performance"])
    
    # Run all tests if no filter specified
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

