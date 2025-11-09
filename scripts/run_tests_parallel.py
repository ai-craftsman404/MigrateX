"""
Test execution script for running all test agents in parallel
Integrates with acceptance criteria system to record test results.
"""

import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime
from migratex.core.context import MigrationContext
from migratex.testing.test_executor_with_acceptance import TestExecutorWithAcceptanceCriteria


def run_test_category(category: str, test_dir: Path = Path("tests"), record_acceptance: bool = True) -> dict:
    """
    Run tests for a specific category.
    Records results as part of acceptance criteria if record_acceptance is True.
    """
    print(f"\n{'='*60}")
    print(f"Running {category.upper()} tests...")
    print(f"{'='*60}")
    
    category_map = {
        "unit": "tests/unit",
        "integration": "tests/integration",
        "e2e": "tests/e2e",
        "edge_case": "tests/edge_cases",
        "outlier": "tests/outliers",
        "performance": "tests/performance",
        "pattern": "tests/unit/test_pattern_detection.py",
        "transformation": "tests/unit/test_transformation.py",
        "outlier_detection": "tests/unit/test_outlier_detection.py",
        "file_operations": "tests/unit/test_file_operations.py",
        "cli": "tests/unit/test_cli.py",
        # New accuracy test categories
        "pattern_detection": "tests/pattern_detection",
        "transformation_accuracy": "tests/transformation",
        "error_recovery": "tests/error_recovery"
    }
    
    test_path = category_map.get(category, f"tests/{category}")
    full_path = Path(test_path)
    
    if not full_path.exists():
        result = {
            "category": category,
            "status": "skipped",
            "reason": f"Test path not found: {full_path}"
        }
        if record_acceptance:
            # Record skipped as not met
            context = MigrationContext(project_path=Path("."), mode="analyze")
            executor = TestExecutorWithAcceptanceCriteria(context)
            # Mark as not met since tests don't exist
            executor.task_manager.start_task(
                f"{category}_tests",
                f"{category.title()} Tests",
                f"Run {category} tests",
                acceptance_criteria=[f"{category}_tests_available"]
            )
            executor.task_manager.mark_criterion_not_met(f"{category}_tests_available")
            executor.task_manager.complete_task(success=False)
        return result
    
    # Use acceptance criteria executor if requested
    if record_acceptance:
        context = MigrationContext(project_path=Path("."), mode="analyze")
        executor = TestExecutorWithAcceptanceCriteria(context)
        
        if category in ["unit", "pattern", "transformation", "outlier_detection", "file_operations", "cli", 
                         "pattern_detection", "transformation_accuracy", "error_recovery"]:
            return executor.run_unit_tests(full_path, f"{category}_tests")
        elif category == "integration":
            return executor.run_integration_tests(full_path, f"{category}_tests")
        elif category == "e2e":
            return executor.run_e2e_tests(full_path, f"{category}_tests")
    
    # Fallback to direct pytest execution
    cmd = [
        sys.executable, "-m", "pytest",
        str(full_path),
        "-v",
        "--tb=short",
        "--junit-xml", f"test-results-{category}.xml",
        "--cov=migratex" if category == "unit" else "",
        "--cov-report=json" if category == "unit" else "",
        "--cov-report=term" if category == "unit" else "",
    ]
    
    # Remove empty strings
    cmd = [c for c in cmd if c]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        return {
            "category": category,
            "status": "completed" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "tests_run": _parse_test_count(result.stdout),
            "tests_passed": _parse_passed_count(result.stdout),
            "tests_failed": _parse_failed_count(result.stdout),
        }
    except subprocess.TimeoutExpired:
        return {
            "category": category,
            "status": "timeout",
            "error": "Test execution exceeded timeout"
        }
    except Exception as e:
        return {
            "category": category,
            "status": "error",
            "error": str(e)
        }


def _parse_test_count(output: str) -> int:
    """Parse total test count from pytest output."""
    import re
    match = re.search(r'(\d+)\s+passed', output)
    return int(match.group(1)) if match else 0


def _parse_passed_count(output: str) -> int:
    """Parse passed test count from pytest output."""
    import re
    match = re.search(r'(\d+)\s+passed', output)
    return int(match.group(1)) if match else 0


def _parse_failed_count(output: str) -> int:
    """Parse failed test count from pytest output."""
    import re
    match = re.search(r'(\d+)\s+failed', output)
    return int(match.group(1)) if match else 0


def run_all_tests_parallel(num_workers: int = 8, record_acceptance: bool = True) -> dict:
    """Run all test categories in parallel."""
    categories = [
        "pattern",
        "transformation",
        "outlier_detection",
        "unit",
        "integration",
        "e2e",
        "edge_case",
        "outlier",
        "performance",
        # New accuracy test categories
        "pattern_detection",
        "transformation_accuracy",
        "error_recovery"
    ]
    
    print(f"\n{'='*60}")
    print(f"PARALLEL TEST EXECUTION")
    print(f"{'='*60}")
    print(f"Categories: {len(categories)}")
    print(f"Workers: {num_workers}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    results = []
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_category = {
            executor.submit(run_test_category, cat, test_dir, record_acceptance): cat
            for cat in categories
        }
        
        for future in as_completed(future_to_category):
            category = future_to_category[future]
            try:
                result = future.result()
                results.append(result)
                
                # Record acceptance criteria if enabled
                if record_acceptance and result.get("status") == "completed":
                    print(f"  ✓ Acceptance criteria met for {category}")
                elif record_acceptance and result.get("status") == "failed":
                    print(f"  ✗ Acceptance criteria NOT met for {category}")
                
                status_icon = "✓" if result["status"] == "completed" else "✗"
                print(f"{status_icon} {category:20s} - {result['status']:10s} "
                      f"(Passed: {result.get('tests_passed', 0)}, "
                      f"Failed: {result.get('tests_failed', 0)})")
            except Exception as e:
                results.append({
                    "category": category,
                    "status": "error",
                    "error": str(e)
                })
                print(f"✗ {category:20s} - ERROR: {e}")
    
    # Generate summary
    total_tests = sum(r.get("tests_run", 0) for r in results)
    total_passed = sum(r.get("tests_passed", 0) for r in results)
    total_failed = sum(r.get("tests_failed", 0) for r in results)
    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] == "failed")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "num_categories": len(categories),
        "num_workers": num_workers,
        "total_tests_run": total_tests,
        "total_tests_passed": total_passed,
        "total_tests_failed": total_failed,
        "categories_completed": completed,
        "categories_failed": failed,
        "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "overall_status": "passed" if total_failed == 0 and failed == 0 else "failed",
        "results": results
    }
    
    print(f"\n{'='*60}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests Run: {total_tests}")
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Categories Completed: {completed}/{len(categories)}")
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"{'='*60}\n")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests in parallel")
    parser.add_argument("--category", type=str, help="Run specific category")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--output", type=str, default="parallel-test-results.json", help="Output file")
    parser.add_argument("--no-acceptance", action="store_true", help="Don't record acceptance criteria")
    
    args = parser.parse_args()
    
    record_acceptance = not args.no_acceptance
    
    if args.category:
        # Run single category
        result = run_test_category(args.category, record_acceptance=record_acceptance)
        print(json.dumps(result, indent=2))
    else:
        # Run all categories in parallel
        summary = run_all_tests_parallel(num_workers=args.workers, record_acceptance=record_acceptance)
        
        # Save results
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"Results saved to: {output_path}")
        
        # Exit with error code if tests failed
        if summary["overall_status"] == "failed":
            sys.exit(1)

