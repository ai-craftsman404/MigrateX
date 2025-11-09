"""
Task management with testing acceptance criteria
"""

from migratex.testing.results_tracker import testing_tracker
from pathlib import Path
from typing import Dict, Any, Optional, List


class TaskManager:
    """
    Manages tasks with testing results as part of acceptance criteria.
    Every task must have testing results recorded.
    """
    
    def __init__(self, context):
        self.context = context
        self.tracker = context.testing_tracker
    
    def start_task(self, task_id: str, task_name: str, description: str, acceptance_criteria: List[str]):
        """
        Start a new task with acceptance criteria.
        All acceptance criteria must include testing validation.
        """
        self.tracker.start_task(task_id, task_name, description)
        self.context.current_task_id = task_id
        
        # Record acceptance criteria
        for criterion in acceptance_criteria:
            self.tracker.mark_acceptance_criteria(task_id, criterion, met=False)
        
        return task_id
    
    def record_test_results(self, task_id: Optional[str] = None, **kwargs):
        """
        Record test results for current or specified task.
        All test types should be recorded.
        """
        task_id = task_id or self.context.current_task_id
        if not task_id:
            return
        
        if "unit_passed" in kwargs:
            self.tracker.record_unit_test_result(
                task_id,
                kwargs["unit_passed"],
                kwargs.get("unit_failed", 0),
                kwargs.get("unit_total", kwargs["unit_passed"])
            )
        
        if "integration_passed" in kwargs:
            self.tracker.record_integration_test_result(
                task_id,
                kwargs["integration_passed"],
                kwargs.get("integration_failed", 0),
                kwargs.get("integration_total", kwargs["integration_passed"])
            )
        
        if "e2e_passed" in kwargs:
            self.tracker.record_e2e_test_result(
                task_id,
                kwargs["e2e_passed"],
                kwargs.get("e2e_failed", 0),
                kwargs.get("e2e_total", kwargs["e2e_passed"])
            )
        
        if "validation_passed" in kwargs:
            self.tracker.record_validation_result(
                task_id,
                kwargs["validation_passed"],
                kwargs.get("validation_failed", 0),
                kwargs.get("validation_total", kwargs["validation_passed"])
            )
    
    def mark_criterion_met(self, criterion: str, task_id: Optional[str] = None, requires_review: bool = False):
        """Mark an acceptance criterion as met."""
        task_id = task_id or self.context.current_task_id
        if task_id:
            self.tracker.mark_acceptance_criteria(task_id, criterion, met=True, requires_review=requires_review)
    
    def mark_criterion_not_met(self, criterion: str, task_id: Optional[str] = None):
        """Mark an acceptance criterion as not met."""
        task_id = task_id or self.context.current_task_id
        if task_id:
            self.tracker.mark_acceptance_criteria(task_id, criterion, met=False)
    
    def add_error(self, task_id: Optional[str], error: str):
        """Add an error to a task."""
        task_id = task_id or self.context.current_task_id
        if task_id:
            self.tracker.add_error(task_id, error)
    
    def complete_task(self, task_id: Optional[str] = None, success: Optional[bool] = None):
        """
        Complete a task. Success is determined by acceptance criteria.
        If success not specified, checks if all criteria are met.
        """
        task_id = task_id or self.context.current_task_id
        if not task_id:
            return
        
        if success is None:
            # Determine success from acceptance criteria
            results = self.tracker.get_task_results(task_id)
            if results:
                ac = results["acceptance_criteria"]
                # Task succeeds if all criteria met and none failed
                success = (
                    len(ac["met"]) > 0 and
                    len(ac["not_met"]) == 0 and
                    len(results["errors"]) == 0
                )
            else:
                success = False
        
        self.tracker.complete_task(task_id, success)
        self.context.current_task_id = None
    
    def get_task_status(self, task_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get current status of a task including testing results."""
        task_id = task_id or self.context.current_task_id
        if task_id:
            return self.tracker.get_task_results(task_id)
        return None
    
    def generate_testing_report(self, output_path: Path):
        """Generate comprehensive testing report for all tasks."""
        self.tracker.save_summary_report(output_path)

