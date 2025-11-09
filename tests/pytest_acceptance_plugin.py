"""
Pytest plugin for automatic test result recording and acceptance criteria tracking.

This plugin ensures every test automatically records results and tracks acceptance criteria.
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from migratex.core.context import MigrationContext
from migratex.core.task_manager import TaskManager
from migratex.testing.results_tracker import testing_tracker


# Track test categories and their acceptance criteria
TEST_CATEGORIES = {
    "unit": {
        "task_id_prefix": "unit_test",
        "acceptance_criteria": [
            "unit_tests_all_passed",
            "unit_test_coverage_adequate",
            "no_unit_test_errors",
            "unit_test_assertions_strong"
        ]
    },
    "integration": {
        "task_id_prefix": "integration_test",
        "acceptance_criteria": [
            "integration_tests_all_passed",
            "integration_test_scenarios_covered",
            "no_integration_test_errors",
            "integration_test_outcomes_verified"
        ]
    },
    "e2e": {
        "task_id_prefix": "e2e_test",
        "acceptance_criteria": [
            "e2e_tests_all_passed",
            "e2e_critical_paths_covered",
            "no_e2e_test_errors",
            "e2e_test_outcomes_verified",
            "e2e_test_files_transformed",
            "e2e_test_git_integration_works"
        ]
    },
    "edge_cases": {
        "task_id_prefix": "edge_case_test",
        "acceptance_criteria": [
            "edge_case_tests_all_passed",
            "edge_cases_covered",
            "no_edge_case_test_errors"
        ]
    },
    "outliers": {
        "task_id_prefix": "outlier_test",
        "acceptance_criteria": [
            "outlier_tests_all_passed",
            "outlier_scenarios_handled",
            "no_outlier_test_errors"
        ]
    },
    "performance": {
        "task_id_prefix": "performance_test",
        "acceptance_criteria": [
            "performance_tests_all_passed",
            "performance_benchmarks_met",
            "no_performance_test_errors"
        ]
    },
    "windows": {
        "task_id_prefix": "windows_test",
        "acceptance_criteria": [
            "windows_tests_all_passed",
            "windows_compatibility_verified",
            "no_windows_test_errors",
            "windows_console_encoding_safe"
        ]
    },
    "error_recovery": {
        "task_id_prefix": "error_recovery_test",
        "acceptance_criteria": [
            "error_recovery_tests_all_passed",
            "error_scenarios_handled",
            "no_error_recovery_test_errors"
        ]
    },
    "transformation": {
        "task_id_prefix": "transformation_test",
        "acceptance_criteria": [
            "transformation_tests_all_passed",
            "transformation_accuracy_verified",
            "no_transformation_test_errors",
            "transformation_outcomes_verified"
        ]
    },
    "pattern_detection": {
        "task_id_prefix": "pattern_detection_test",
        "acceptance_criteria": [
            "pattern_detection_tests_all_passed",
            "pattern_detection_accuracy_verified",
            "no_pattern_detection_test_errors"
        ]
    }
}


def get_test_category(test_path: Path) -> str:
    """Determine test category from test file path."""
    parts = test_path.parts
    if "unit" in parts:
        return "unit"
    elif "integration" in parts:
        return "integration"
    elif "e2e" in parts:
        return "e2e"
    elif "edge_cases" in parts or "edge_case" in parts:
        return "edge_cases"
    elif "outliers" in parts or "outlier" in parts:
        return "outliers"
    elif "performance" in parts:
        return "performance"
    elif "windows" in parts:
        return "windows"
    elif "error_recovery" in parts or "error_recovery" in parts:
        return "error_recovery"
    elif "transformation" in parts:
        return "transformation"
    elif "pattern_detection" in parts or "pattern" in parts:
        return "pattern_detection"
    else:
        return "unit"  # Default


@pytest.fixture(scope="module")
def test_task_context(request):
    """
    Create a task context for each test module with acceptance criteria.
    Automatically records test results for the module.
    """
    test_file = Path(request.fspath)
    category = get_test_category(test_file)
    category_config = TEST_CATEGORIES.get(category, TEST_CATEGORIES["unit"])
    
    # Create unique task ID based on test file
    task_id = f"{category_config['task_id_prefix']}_{test_file.stem}"
    
    # Create minimal context for task manager (must match MigrationContext interface)
    class TestContext:
        def __init__(self):
            self.testing_tracker = testing_tracker
            self.current_task_id = task_id
            self.verbose = False
            self.project_path = test_file.parent  # Dummy path for compatibility
            # Add all MigrationContext attributes that might be accessed
            self.git_root = None
            self.original_branch = None
            self.use_git_branch = False
            self.git_branch_name = "migratex/migrate-to-maf"
            self.auto_create_branch = True
            self.show_git_diff = True
            self.report = {}
            self.updated_files = []
            self.failed_files = []
            self.patterns_applied = []
            self.mode = "analyze"
            self.output_dir = None
            # Add pattern_library for compatibility
            from migratex.patterns.library import PatternLibrary
            self.pattern_library = PatternLibrary()
        
        def get_task_manager(self):
            """Get task manager instance (matches MigrationContext interface)."""
            from migratex.core.task_manager import TaskManager
            return TaskManager(self)
        
        def get_checkpoint(self):
            """Get checkpoint (matches MigrationContext interface)."""
            return {
                "updated_files": self.updated_files,
                "failed_files": self.failed_files,
                "patterns_applied": self.patterns_applied,
                "total_files": len(self.updated_files) + len(self.failed_files)
            }
        
        def load_patterns(self):
            """Load patterns (matches MigrationContext interface)."""
            # No-op for test context
            pass
    
    context = TestContext()
    task_manager = TaskManager(context)
    
    # Start task with acceptance criteria
    task_manager.start_task(
        task_id,
        f"{category.title()} Tests: {test_file.stem}",
        f"Test module: {test_file.name}",
        acceptance_criteria=category_config["acceptance_criteria"]
    )
    
    # Store in request for cleanup
    request.module._task_id = task_id
    request.module._task_manager = task_manager
    request.module._test_category = category
    
    yield {
        "task_id": task_id,
        "task_manager": task_manager,
        "category": category,
        "context": context
    }
    
    # Complete task will be done in pytest_runtest_makereport hook


@pytest.fixture(scope="function")
def record_test_result(request):
    """
    Record individual test result with acceptance criteria verification.
    """
    test_name = request.node.name
    test_category = getattr(request.module, "_test_category", "unit")
    
    def _record_result(passed: bool, **kwargs):
        """Record test result with additional metadata."""
        task_id = getattr(request.module, "_task_id", None)
        if not task_id:
            return
        
        task_manager = getattr(request.module, "_task_manager", None)
        if not task_manager:
            return
        
        # Record based on category
        if test_category == "unit":
            task_manager.record_test_results(
                unit_passed=1 if passed else 0,
                unit_failed=0 if passed else 1,
                unit_total=1
            )
        elif test_category == "integration":
            task_manager.record_test_results(
                integration_passed=1 if passed else 0,
                integration_failed=0 if passed else 1,
                integration_total=1
            )
        elif test_category == "e2e":
            task_manager.record_test_results(
                e2e_passed=1 if passed else 0,
                e2e_failed=0 if passed else 1,
                e2e_total=1
            )
        
        # Mark acceptance criteria based on test outcome
        if passed:
            # Verify strong assertions if specified
            if kwargs.get("strong_assertion", False):
                task_manager.mark_criterion_met(f"{test_category}_test_assertions_strong")
            
            # Verify outcomes if specified
            if kwargs.get("outcome_verified", False):
                task_manager.mark_criterion_met(f"{test_category}_test_outcomes_verified")
        else:
            # Mark criteria as not met
            category_config = TEST_CATEGORIES.get(test_category, TEST_CATEGORIES["unit"])
            for criterion in category_config["acceptance_criteria"]:
                task_manager.mark_criterion_not_met(criterion)
    
    return _record_result


def pytest_runtest_makereport(item, call):
    """
    Hook to record test results automatically after each test.
    """
    if call.when == "call":  # Only record on actual test execution
        test_category = get_test_category(Path(item.fspath))
        task_id = getattr(item.module, "_task_id", None)
        task_manager = getattr(item.module, "_task_manager", None)
        
        if task_id and task_manager:
            passed = call.excinfo is None
            
            # Record result based on category
            if test_category == "unit":
                task_manager.record_test_results(
                    unit_passed=1 if passed else 0,
                    unit_failed=0 if passed else 1,
                    unit_total=1
                )
            elif test_category == "integration":
                task_manager.record_test_results(
                    integration_passed=1 if passed else 0,
                    integration_failed=0 if passed else 1,
                    integration_total=1
                )
            elif test_category == "e2e":
                task_manager.record_test_results(
                    e2e_passed=1 if passed else 0,
                    e2e_failed=0 if passed else 1,
                    e2e_total=1
                )
            
            # Mark acceptance criteria
            category_config = TEST_CATEGORIES.get(test_category, TEST_CATEGORIES["unit"])
            if passed:
                # Mark "all_passed" criteria will be updated at module level
                pass
            else:
                # Mark criteria as not met on failure
                for criterion in category_config["acceptance_criteria"]:
                    if "all_passed" in criterion:
                        task_manager.mark_criterion_not_met(criterion)


def pytest_sessionfinish(session, exitstatus):
    """
    Complete all tasks and generate summary report at end of test session.
    """
    # Complete all tasks
    all_results = testing_tracker.get_all_results()
    for task_id, result in all_results.items():
        if result["status"] == "in_progress":
            # Check if all tests passed
            test_results = result["testing_results"]
            all_passed = True
            
            for test_type in ["unit_tests", "integration_tests", "e2e_tests"]:
                test_data = test_results.get(test_type, {})
                if test_data.get("run", False):
                    if test_data.get("failed", 0) > 0:
                        all_passed = False
            
            testing_tracker.complete_task(task_id, success=all_passed)
    
    # Generate summary report
    summary = testing_tracker.generate_summary_report()
    summary_path = Path("testing_results") / "test_session_summary.json"
    summary_path.parent.mkdir(exist_ok=True)
    testing_tracker.save_summary_report(summary_path)
    
    if session.config.option.verbose >= 1:
        print(f"\n[TEST RESULTS] Summary saved to: {summary_path}")
        print(f"[TEST RESULTS] Total tasks: {summary['total_tasks']}")
        print(f"[TEST RESULTS] Completed: {summary['completed']}")
        print(f"[TEST RESULTS] Failed: {summary['failed']}")


@pytest.fixture(scope="function")
def verify_outcome(request):
    """
    Helper fixture to verify test outcomes and mark acceptance criteria.
    Use this in tests to ensure outcomes are verified.
    """
    def _verify(condition: bool, message: str = "", criterion: Optional[str] = None):
        """Verify an outcome condition."""
        task_manager = getattr(request.module, "_task_manager", None)
        test_category = getattr(request.module, "_test_category", "unit")
        
        if condition:
            if criterion:
                if task_manager:
                    task_manager.mark_criterion_met(criterion)
            else:
                # Auto-determine criterion based on category
                if test_category == "e2e":
                    if task_manager:
                        task_manager.mark_criterion_met("e2e_test_outcomes_verified")
                elif test_category == "integration":
                    if task_manager:
                        task_manager.mark_criterion_met("integration_test_outcomes_verified")
        else:
            assert False, f"Outcome verification failed: {message}"
        
        return condition
    
    return _verify


@pytest.fixture(scope="function")
def verify_strong_assertion(request):
    """
    Helper fixture to mark that a test uses strong assertions.
    """
    task_manager = getattr(request.module, "_task_manager", None)
    test_category = getattr(request.module, "_test_category", "unit")
    
    if task_manager:
        criterion = f"{test_category}_test_assertions_strong"
        task_manager.mark_criterion_met(criterion)
    
    return True

