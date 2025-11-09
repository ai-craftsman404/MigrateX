#!/usr/bin/env python3
"""
Parallel Test Execution Script with Acceptance Criteria Validation

Runs all tests in parallel and validates results methodically.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import time


def run_tests_parallel(category: str = None, max_workers: str = "auto") -> Dict[str, Any]:
    """Run tests in parallel for a category."""
    test_path = f"tests/{category}" if category else "tests"
    
    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        "-n", max_workers,
        "-v",
        "--tb=short",
        "--junit-xml", f"test-results-{category or 'all'}.xml",
        "--no-cov",  # Disable coverage for faster execution
    ]
    
    print(f"\n[RUNNING] {category or 'All tests'} with {max_workers} workers...")
    start_time = time.time()
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=3600  # 1 hour timeout
    )
    
    elapsed = time.time() - start_time
    
    # Parse results
    passed = parse_count(result.stdout, r'(\d+)\s+passed')
    failed = parse_count(result.stdout, r'(\d+)\s+failed')
    errors = parse_count(result.stdout, r'(\d+)\s+error')
    total = passed + failed + errors
    
    return {
        "category": category or "all",
        "exit_code": result.returncode,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "total": total,
        "elapsed": elapsed,
        "success": result.returncode == 0 and failed == 0 and errors == 0,
        "stdout": result.stdout[-5000:] if len(result.stdout) > 5000 else result.stdout,  # Last 5K chars
        "stderr": result.stderr[-5000:] if len(result.stderr) > 5000 else result.stderr
    }


def parse_count(text: str, pattern: str) -> int:
    """Parse count from text using regex pattern."""
    import re
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0


def validate_acceptance_criteria() -> Dict[str, Any]:
    """Validate acceptance criteria from test results."""
    summary_path = Path("testing_results") / "test_session_summary.json"
    
    if not summary_path.exists():
        return {
            "valid": False,
            "error": "Summary file not found",
            "path": str(summary_path)
        }
    
    try:
        with open(summary_path) as f:
            summary = json.load(f)
        
        # Check acceptance criteria
        ac_summary = summary.get("acceptance_criteria_summary", {})
        total_met = ac_summary.get("total_met", 0)
        total_not_met = ac_summary.get("total_not_met", 0)
        total_requires_review = ac_summary.get("total_requires_review", 0)
        
        return {
            "valid": True,
            "total_met": total_met,
            "total_not_met": total_not_met,
            "total_requires_review": total_requires_review,
            "all_met": total_not_met == 0 and total_requires_review == 0,
            "summary": summary
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def main():
    """Main execution function."""
    print("=" * 80)
    print("PARALLEL TEST EXECUTION WITH ACCEPTANCE CRITERIA VALIDATION")
    print("=" * 80)
    
    # Test categories to run
    categories = [
        "unit",
        "integration", 
        "e2e",
        "edge_cases",
        "outliers",
        "performance",
        "windows",
        "error_recovery",
        "transformation",
        "pattern_detection"
    ]
    
    results = {}
    overall_success = True
    
    # Run each category in parallel
    for category in categories:
        category_path = Path(f"tests/{category}")
        if not category_path.exists():
            print(f"\n[SKIP] {category} - directory not found")
            continue
        
        result = run_tests_parallel(category, max_workers="auto")
        results[category] = result
        
        if not result["success"]:
            overall_success = False
        
        status = "[PASS]" if result["success"] else "[FAIL]"
        print(f"{status} {category}: {result['passed']}/{result['total']} passed in {result['elapsed']:.1f}s")
    
    # Validate acceptance criteria
    print("\n" + "=" * 80)
    print("VALIDATING ACCEPTANCE CRITERIA")
    print("=" * 80)
    
    ac_validation = validate_acceptance_criteria()
    
    if ac_validation["valid"]:
        print(f"\nAcceptance Criteria Status:")
        print(f"  Met: {ac_validation['total_met']}")
        print(f"  Not Met: {ac_validation['total_not_met']}")
        print(f"  Requires Review: {ac_validation['total_requires_review']}")
        
        if ac_validation["all_met"]:
            print("\n[SUCCESS] All acceptance criteria met!")
        else:
            print("\n[WARNING] Some acceptance criteria not met")
            overall_success = False
    else:
        print(f"\n[ERROR] Failed to validate acceptance criteria: {ac_validation.get('error', 'Unknown')}")
        overall_success = False
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_passed = sum(r["passed"] for r in results.values())
    total_failed = sum(r["failed"] for r in results.values())
    total_errors = sum(r["errors"] for r in results.values())
    total_tests = sum(r["total"] for r in results.values())
    total_time = sum(r["elapsed"] for r in results.values())
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"  Passed: {total_passed}")
    print(f"  Failed: {total_failed}")
    print(f"  Errors: {total_errors}")
    print(f"  Total Time: {total_time:.1f}s")
    print(f"\nOverall Status: {'[SUCCESS]' if overall_success else '[FAILURE]'}")
    
    # Save results
    results_path = Path("testing_results") / "parallel_execution_results.json"
    results_path.parent.mkdir(exist_ok=True)
    
    with open(results_path, "w") as f:
        json.dump({
            "overall_success": overall_success,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_errors": total_errors,
            "total_time": total_time,
            "category_results": results,
            "acceptance_criteria": ac_validation
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_path}")
    
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())

