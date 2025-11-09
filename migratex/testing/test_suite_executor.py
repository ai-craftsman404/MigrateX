"""
Test suite execution module - Implements standard test tasks T1-T6
"""

from pathlib import Path
from typing import Dict, List, Any
import subprocess
import json
import shutil


class TestSuiteExecutor:
    """
    Executes standard test tasks (T1-T6) for repository validation.
    Based on comprehensive test suite plan.
    """
    
    def __init__(self, repo_path: Path, repo_info: Dict[str, str]):
        self.repo_path = repo_path
        self.repo_info = repo_info
        self.results = {
            "repo": repo_info["name"],
            "tier": repo_info.get("tier", 0),
            "priority": repo_info.get("priority", "unknown"),
            "tasks": {}
        }
    
    def execute_task_t1_clone_baseline(self) -> Dict[str, Any]:
        """Task T1: Clone & Baseline"""
        result = {
            "task": "T1",
            "status": "pending",
            "baseline_metrics": {}
        }
        
        try:
            # Record baseline metrics
            python_files = list(self.repo_path.rglob("*.py"))
            result["baseline_metrics"] = {
                "python_files": len(python_files),
                "repo_path": str(self.repo_path)
            }
            
            # Try to run existing tests if available
            # This is optional and may fail if no tests exist
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.results["tasks"]["T1"] = result
        return result
    
    def execute_task_t2_analyze(self) -> Dict[str, Any]:
        """Task T2: Discovery / Analyze Phase"""
        result = {
            "task": "T2",
            "status": "pending",
            "report_path": None,
            "patterns_detected": []
        }
        
        try:
            from migratex.core.context import MigrationContext
            from migratex.core.orchestrator import Orchestrator
            
            report_path = self.repo_path / "migration-report.json"
            
            context = MigrationContext(
                project_path=self.repo_path,
                mode="analyze",
                verbose=False
            )
            
            orchestrator = Orchestrator(context)
            orchestrator.run_analysis()
            
            report = context.get_report()
            
            # Save report
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
            
            result["report_path"] = str(report_path)
            result["patterns_detected"] = report.get("patterns", [])
            result["status"] = "completed"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.results["tasks"]["T2"] = result
        return result
    
    def execute_task_t3_auto_mode(self) -> Dict[str, Any]:
        """Task T3: Auto Mode (High-Confidence Only)"""
        result = {
            "task": "T3",
            "status": "pending",
            "files_changed": [],
            "syntax_errors": []
        }
        
        try:
            from migratex.core.context import MigrationContext
            from migratex.core.orchestrator import Orchestrator
            
            context = MigrationContext(
                project_path=self.repo_path,
                mode="auto",
                error_policy="continue"
            )
            
            orchestrator = Orchestrator(context)
            orchestrator.run_apply_auto()
            
            checkpoint = context.get_checkpoint()
            result["files_changed"] = checkpoint.get("updated_files", [])
            result["status"] = "completed"
            
            # Check for syntax errors (basic validation)
            # TODO: Run linters/compilers on changed files
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.results["tasks"]["T3"] = result
        return result
    
    def execute_task_t4_review_mode(self) -> Dict[str, Any]:
        """Task T4: Review Mode (Spot Check)"""
        result = {
            "task": "T4",
            "status": "pending",
            "patterns_prompted": [],
            "decisions_made": []
        }
        
        # This would require interactive mode
        # For automated testing, we can simulate or skip
        result["status"] = "skipped"  # Requires manual interaction
        result["note"] = "Review mode requires manual interaction"
        
        self.results["tasks"]["T4"] = result
        return result
    
    def execute_task_t5_validation(self) -> Dict[str, Any]:
        """Task T5: Post-Migration Validation"""
        result = {
            "task": "T5",
            "status": "pending",
            "tests_run": False,
            "tests_passed": None,
            "tests_failed": None
        }
        
        try:
            # Try to run pytest if available
            if (self.repo_path / "pytest.ini").exists() or (self.repo_path / "tests").exists():
                test_result = subprocess.run(
                    ["pytest", str(self.repo_path)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                result["tests_run"] = True
                result["exit_code"] = test_result.returncode
                result["status"] = "completed" if test_result.returncode == 0 else "failed"
            else:
                result["status"] = "skipped"
                result["note"] = "No test suite found"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.results["tasks"]["T5"] = result
        return result
    
    def execute_task_t6_checkpoints(self) -> Dict[str, Any]:
        """Task T6: Logging & Checkpoints"""
        result = {
            "task": "T6",
            "status": "pending",
            "files_generated": []
        }
        
        try:
            # Check for expected output files
            expected_files = [
                "migration-report.json",
                "migration-results.json",
                "pattern-cache.yaml"
            ]
            
            for filename in expected_files:
                file_path = self.repo_path / filename
                if file_path.exists():
                    result["files_generated"].append(filename)
            
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self.results["tasks"]["T6"] = result
        return result
    
    def execute_all_tasks(self) -> Dict[str, Any]:
        """Execute all standard test tasks T1-T6."""
        self.execute_task_t1_clone_baseline()
        self.execute_task_t2_analyze()
        self.execute_task_t3_auto_mode()
        self.execute_task_t4_review_mode()
        self.execute_task_t5_validation()
        self.execute_task_t6_checkpoints()
        
        return self.results

