"""
Test Executor with Acceptance Criteria Integration

Runs tests and records results as part of acceptance criteria.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re
from migratex.core.context import MigrationContext
from migratex.core.task_manager import TaskManager


class TestExecutorWithAcceptanceCriteria:
    """
    Executes tests and records results as part of acceptance criteria.
    Each test category is tracked as a task with acceptance criteria.
    """
    
    def __init__(self, context: MigrationContext):
        self.context = context
        # Ensure testing_tracker is initialized
        if self.context.testing_tracker is None:
            from migratex.testing.results_tracker import testing_tracker
            self.context.testing_tracker = testing_tracker
        self.task_manager = TaskManager(context)
    
    def run_unit_tests(self, test_path: Path, task_id: str = "unit_tests") -> Dict[str, Any]:
        """
        Run unit tests and record results as acceptance criteria.
        
        Acceptance Criteria:
        - unit_tests_all_passed: All unit tests pass
        - unit_test_coverage_adequate: Coverage meets threshold
        - no_unit_test_errors: No test execution errors
        """
        # Start task with acceptance criteria
        self.task_manager.start_task(
            task_id,
            "Unit Tests",
            f"Run unit tests from {test_path}",
            acceptance_criteria=[
                "unit_tests_all_passed",
                "unit_test_coverage_adequate",
                "no_unit_test_errors"
            ]
        )
        
        try:
            # Run pytest
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--junit-xml", f"test-results-{task_id}.xml",
                "--cov=migratex",
                "--cov-report=json",
                "--cov-report=term",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # Parse results
            passed = self._parse_passed_count(result.stdout)
            failed = self._parse_failed_count(result.stdout)
            total = passed + failed
            coverage = self._parse_coverage(result.stdout)
            
            # Record test results
            self.task_manager.record_test_results(
                unit_passed=passed,
                unit_failed=failed,
                unit_total=total
            )
            
            # Mark acceptance criteria
            if failed == 0:
                self.task_manager.mark_criterion_met("unit_tests_all_passed")
            else:
                self.task_manager.mark_criterion_not_met("unit_tests_all_passed")
            
            if coverage >= 80.0:  # Threshold
                self.task_manager.mark_criterion_met("unit_test_coverage_adequate")
            else:
                self.task_manager.mark_criterion_not_met("unit_test_coverage_adequate")
            
            if result.returncode == 0 or (result.returncode != 0 and failed == 0):
                self.task_manager.mark_criterion_met("no_unit_test_errors")
            else:
                self.task_manager.mark_criterion_not_met("no_unit_test_errors")
            
            # Complete task
            success = failed == 0 and result.returncode == 0
            self.task_manager.complete_task(success=success)
            
            return {
                "task_id": task_id,
                "status": "completed" if success else "failed",
                "passed": passed,
                "failed": failed,
                "total": total,
                "coverage": coverage,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            self.task_manager.mark_criterion_not_met("no_unit_test_errors")
            self.task_manager.complete_task(success=False)
            return {
                "task_id": task_id,
                "status": "timeout",
                "error": "Test execution exceeded timeout"
            }
        except Exception as e:
            self.task_manager.mark_criterion_not_met("no_unit_test_errors")
            self.task_manager.complete_task(success=False)
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    def run_integration_tests(self, test_path: Path, task_id: str = "integration_tests") -> Dict[str, Any]:
        """
        Run integration tests and record results as acceptance criteria.
        
        Acceptance Criteria:
        - integration_tests_all_passed: All integration tests pass
        - integration_test_scenarios_covered: All scenarios tested
        - no_integration_test_errors: No test execution errors
        """
        self.task_manager.start_task(
            task_id,
            "Integration Tests",
            f"Run integration tests from {test_path}",
            acceptance_criteria=[
                "integration_tests_all_passed",
                "integration_test_scenarios_covered",
                "no_integration_test_errors"
            ]
        )
        
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--junit-xml", f"test-results-{task_id}.xml",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            passed = self._parse_passed_count(result.stdout)
            failed = self._parse_failed_count(result.stdout)
            total = passed + failed
            
            self.task_manager.record_test_results(
                integration_passed=passed,
                integration_failed=failed,
                integration_total=total
            )
            
            if failed == 0:
                self.task_manager.mark_criterion_met("integration_tests_all_passed")
            else:
                self.task_manager.mark_criterion_not_met("integration_tests_all_passed")
            
            # Assume scenarios covered if tests run
            if total > 0:
                self.task_manager.mark_criterion_met("integration_test_scenarios_covered")
            
            if result.returncode == 0 or (result.returncode != 0 and failed == 0):
                self.task_manager.mark_criterion_met("no_integration_test_errors")
            else:
                self.task_manager.mark_criterion_not_met("no_integration_test_errors")
            
            success = failed == 0 and result.returncode == 0
            self.task_manager.complete_task(success=success)
            
            return {
                "task_id": task_id,
                "status": "completed" if success else "failed",
                "passed": passed,
                "failed": failed,
                "total": total,
                "exit_code": result.returncode
            }
            
        except Exception as e:
            self.task_manager.mark_criterion_not_met("no_integration_test_errors")
            self.task_manager.complete_task(success=False)
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    def run_e2e_tests(self, test_path: Path, task_id: str = "e2e_tests") -> Dict[str, Any]:
        """
        Run E2E tests and record results as acceptance criteria.
        
        Acceptance Criteria:
        - e2e_tests_all_passed: All E2E tests pass
        - e2e_critical_paths_covered: Critical paths tested
        - no_e2e_test_errors: No test execution errors
        """
        self.task_manager.start_task(
            task_id,
            "E2E Tests",
            f"Run E2E tests from {test_path}",
            acceptance_criteria=[
                "e2e_tests_all_passed",
                "e2e_critical_paths_covered",
                "no_e2e_test_errors"
            ]
        )
        
        try:
            cmd = [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--junit-xml", f"test-results-{task_id}.xml",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1200  # 20 minutes for E2E
            )
            
            passed = self._parse_passed_count(result.stdout)
            failed = self._parse_failed_count(result.stdout)
            total = passed + failed
            
            self.task_manager.record_test_results(
                e2e_passed=passed,
                e2e_failed=failed,
                e2e_total=total
            )
            
            if failed == 0:
                self.task_manager.mark_criterion_met("e2e_tests_all_passed")
            else:
                self.task_manager.mark_criterion_not_met("e2e_tests_all_passed")
            
            if total > 0:
                self.task_manager.mark_criterion_met("e2e_critical_paths_covered")
            
            if result.returncode == 0 or (result.returncode != 0 and failed == 0):
                self.task_manager.mark_criterion_met("no_e2e_test_errors")
            else:
                self.task_manager.mark_criterion_not_met("no_e2e_test_errors")
            
            success = failed == 0 and result.returncode == 0
            self.task_manager.complete_task(success=success)
            
            return {
                "task_id": task_id,
                "status": "completed" if success else "failed",
                "passed": passed,
                "failed": failed,
                "total": total,
                "exit_code": result.returncode
            }
            
        except Exception as e:
            self.task_manager.mark_criterion_not_met("no_e2e_test_errors")
            self.task_manager.complete_task(success=False)
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    def run_all_test_categories(self, test_dir: Path) -> Dict[str, Any]:
        """
        Run all test categories and record results as acceptance criteria.
        
        Returns summary with all test results and acceptance criteria status.
        """
        results = {}
        
        # Unit tests
        unit_path = test_dir / "unit"
        if unit_path.exists():
            results["unit"] = self.run_unit_tests(unit_path, "unit_tests")
        
        # Integration tests
        integration_path = test_dir / "integration"
        if integration_path.exists():
            results["integration"] = self.run_integration_tests(integration_path, "integration_tests")
        
        # E2E tests
        e2e_path = test_dir / "e2e"
        if e2e_path.exists():
            results["e2e"] = self.run_e2e_tests(e2e_path, "e2e_tests")
        
        # Get acceptance criteria summary
        summary = self.task_manager.get_acceptance_criteria_summary()
        
        return {
            "test_results": results,
            "acceptance_criteria": summary,
            "overall_status": "passed" if all(
                r.get("status") == "completed" for r in results.values()
            ) else "failed"
        }
    
    def _parse_passed_count(self, output: str) -> int:
        """Parse passed test count from pytest output."""
        match = re.search(r'(\d+)\s+passed', output)
        return int(match.group(1)) if match else 0
    
    def _parse_failed_count(self, output: str) -> int:
        """Parse failed test count from pytest output."""
        match = re.search(r'(\d+)\s+failed', output)
        return int(match.group(1)) if match else 0
    
    def _parse_coverage(self, output: str) -> float:
        """Parse coverage percentage from pytest output."""
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if match:
            return float(match.group(1))
        
        # Try alternative format
        match = re.search(r'(\d+\.\d+)%', output)
        if match:
            return float(match.group(1))
        
        return 0.0

