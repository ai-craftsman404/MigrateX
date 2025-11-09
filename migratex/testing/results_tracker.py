"""
Testing Results Tracker - Records testing results as part of acceptance criteria
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class TestingResultsTracker:
    """
    Tracks testing results for all tasks.
    Every task must have testing results recorded as part of acceptance criteria.
    """
    
    def __init__(self, results_dir: Path = Path("testing_results")):
        self.results_dir = results_dir
        self.results_dir.mkdir(exist_ok=True)
        self.current_task_results: Dict[str, Any] = {}
    
    def start_task(self, task_id: str, task_name: str, description: str):
        """Start tracking a new task."""
        self.current_task_results[task_id] = {
            "task_id": task_id,
            "task_name": task_name,
            "description": description,
            "started_at": datetime.utcnow().isoformat() + "Z",
            "status": "in_progress",
            "testing_results": {
                "unit_tests": {"run": False, "passed": 0, "failed": 0, "total": 0},
                "integration_tests": {"run": False, "passed": 0, "failed": 0, "total": 0},
                "e2e_tests": {"run": False, "passed": 0, "failed": 0, "total": 0},
                "validation_tests": {"run": False, "passed": 0, "failed": 0, "total": 0},
            },
            "acceptance_criteria": {
                "met": [],
                "not_met": [],
                "requires_manual_review": []
            },
            "test_outputs": [],
            "errors": []
        }
    
    def record_unit_test_result(self, task_id: str, passed: int, failed: int, total: int):
        """Record unit test results for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["testing_results"]["unit_tests"] = {
                "run": True,
                "passed": passed,
                "failed": failed,
                "total": total
            }
            self._update_acceptance_criteria(task_id, "unit_tests", passed == total)
    
    def record_integration_test_result(self, task_id: str, passed: int, failed: int, total: int):
        """Record integration test results for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["testing_results"]["integration_tests"] = {
                "run": True,
                "passed": passed,
                "failed": failed,
                "total": total
            }
            self._update_acceptance_criteria(task_id, "integration_tests", passed == total)
    
    def record_e2e_test_result(self, task_id: str, passed: int, failed: int, total: int):
        """Record E2E test results for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["testing_results"]["e2e_tests"] = {
                "run": True,
                "passed": passed,
                "failed": failed,
                "total": total
            }
            self._update_acceptance_criteria(task_id, "e2e_tests", passed == total)
    
    def record_validation_result(self, task_id: str, passed: int, failed: int, total: int):
        """Record validation test results for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["testing_results"]["validation_tests"] = {
                "run": True,
                "passed": passed,
                "failed": failed,
                "total": total
            }
            self._update_acceptance_criteria(task_id, "validation_tests", passed == total)
    
    def add_test_output(self, task_id: str, output_type: str, content: str):
        """Add test output (logs, reports, etc.) for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["test_outputs"].append({
                "type": output_type,
                "content": content,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    
    def add_error(self, task_id: str, error: str):
        """Record an error for a task."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["errors"].append({
                "error": error,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
    
    def mark_acceptance_criteria(self, task_id: str, criterion: str, met: bool, requires_review: bool = False):
        """Mark an acceptance criterion as met or not met."""
        if task_id in self.current_task_results:
            if requires_review:
                if criterion not in self.current_task_results[task_id]["acceptance_criteria"]["requires_manual_review"]:
                    self.current_task_results[task_id]["acceptance_criteria"]["requires_manual_review"].append(criterion)
            elif met:
                if criterion not in self.current_task_results[task_id]["acceptance_criteria"]["met"]:
                    self.current_task_results[task_id]["acceptance_criteria"]["met"].append(criterion)
            else:
                if criterion not in self.current_task_results[task_id]["acceptance_criteria"]["not_met"]:
                    self.current_task_results[task_id]["acceptance_criteria"]["not_met"].append(criterion)
    
    def _update_acceptance_criteria(self, task_id: str, test_type: str, all_passed: bool):
        """Update acceptance criteria based on test results."""
        criterion = f"{test_type}_all_passed"
        self.mark_acceptance_criteria(task_id, criterion, all_passed)
    
    def complete_task(self, task_id: str, success: bool):
        """Mark a task as completed with final status."""
        if task_id in self.current_task_results:
            self.current_task_results[task_id]["status"] = "completed" if success else "failed"
            self.current_task_results[task_id]["completed_at"] = datetime.utcnow().isoformat() + "Z"
            
            # Save task results
            self._save_task_results(task_id)
    
    def _save_task_results(self, task_id: str):
        """Save task results to file."""
        if task_id in self.current_task_results:
            result_file = self.results_dir / f"{task_id}_results.json"
            with open(result_file, "w") as f:
                json.dump(self.current_task_results[task_id], f, indent=2)
    
    def get_task_results(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get results for a specific task."""
        return self.current_task_results.get(task_id)
    
    def get_all_results(self) -> Dict[str, Dict[str, Any]]:
        """Get all task results."""
        return self.current_task_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of all testing results."""
        summary = {
            "total_tasks": len(self.current_task_results),
            "completed": sum(1 for r in self.current_task_results.values() if r["status"] == "completed"),
            "failed": sum(1 for r in self.current_task_results.values() if r["status"] == "failed"),
            "in_progress": sum(1 for r in self.current_task_results.values() if r["status"] == "in_progress"),
            "test_summary": {
                "unit_tests": {"total_passed": 0, "total_failed": 0, "total_run": 0},
                "integration_tests": {"total_passed": 0, "total_failed": 0, "total_run": 0},
                "e2e_tests": {"total_passed": 0, "total_failed": 0, "total_run": 0},
                "validation_tests": {"total_passed": 0, "total_failed": 0, "total_run": 0},
            },
            "acceptance_criteria_summary": {
                "total_met": 0,
                "total_not_met": 0,
                "total_requires_review": 0
            }
        }
        
        for result in self.current_task_results.values():
            # Aggregate test results
            for test_type in ["unit_tests", "integration_tests", "e2e_tests", "validation_tests"]:
                test_result = result["testing_results"][test_type]
                if test_result["run"]:
                    summary["test_summary"][test_type]["total_passed"] += test_result["passed"]
                    summary["test_summary"][test_type]["total_failed"] += test_result["failed"]
                    summary["test_summary"][test_type]["total_run"] += test_result["total"]
            
            # Aggregate acceptance criteria
            ac = result["acceptance_criteria"]
            summary["acceptance_criteria_summary"]["total_met"] += len(ac["met"])
            summary["acceptance_criteria_summary"]["total_not_met"] += len(ac["not_met"])
            summary["acceptance_criteria_summary"]["total_requires_review"] += len(ac["requires_manual_review"])
        
        return summary
    
    def save_summary_report(self, output_path: Path):
        """Save summary report to file."""
        summary = self.generate_summary_report()
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)


# Global instance accessible to all agents
testing_tracker = TestingResultsTracker()

