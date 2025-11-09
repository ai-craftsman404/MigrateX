"""
Repository Testing Infrastructure

Provides utilities for cloning, testing, and validating migrations against real repositories.
"""

import subprocess
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import json


class RepositoryTester:
    """
    Test framework for running migrations against real repositories.
    Handles cloning, isolation, execution, and cleanup.
    """
    
    def __init__(self, repo_url: str, target_dir: Optional[Path] = None, timeout: int = 300):
        """
        Initialize repository tester.
        
        Args:
            repo_url: Git repository URL
            target_dir: Directory to clone into (default: temp directory)
            timeout: Timeout for git operations in seconds
        """
        self.repo_url = repo_url
        self.timeout = timeout
        self.target_dir = target_dir or Path(tempfile.mkdtemp(prefix="migratex_test_"))
        self.repo_path: Optional[Path] = None
        self.cloned = False
    
    def clone_repository(self) -> Path:
        """
        Clone repository for testing.
        
        Returns:
            Path to cloned repository
        
        Raises:
            RuntimeError: If cloning fails
        """
        if self.cloned and self.repo_path:
            return self.repo_path
        
        repo_name = self.repo_url.split("/")[-1].replace(".git", "")
        self.repo_path = self.target_dir / repo_name
        
        # Remove existing clone if present
        if self.repo_path.exists():
            shutil.rmtree(self.repo_path)
        
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", self.repo_url, str(self.repo_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to clone repository: {result.stderr}")
            
            self.cloned = True
            return self.repo_path
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Repository cloning timed out after {self.timeout}s")
        except FileNotFoundError:
            raise RuntimeError("Git is not installed or not in PATH")
    
    def run_migration_test(self, test_scenario: str, **kwargs) -> Dict[str, Any]:
        """
        Run a migration test scenario.
        
        Args:
            test_scenario: Name of test scenario (analyze, apply_auto, apply_review, etc.)
            **kwargs: Additional arguments for migration
        
        Returns:
            Test results dictionary
        """
        if not self.cloned or not self.repo_path:
            self.clone_repository()
        
        from migratex.core.context import MigrationContext
        from migratex.core.orchestrator import Orchestrator
        
        start_time = time.time()
        result = {
            "scenario": test_scenario,
            "repo_url": self.repo_url,
            "repo_path": str(self.repo_path),
            "success": False,
            "error": None,
            "duration": 0,
            "files_updated": 0,
            "files_failed": 0
        }
        
        try:
            context = MigrationContext(
                project_path=self.repo_path,
                mode=kwargs.get("mode", "analyze"),
                verbose=kwargs.get("verbose", False),
                use_git_branch=kwargs.get("use_git_branch", True),
                git_branch_name=kwargs.get("git_branch_name", "migratex/test-migration")
            )
            
            orchestrator = Orchestrator(context)
            
            if test_scenario == "analyze":
                orchestrator.run_analysis()
            elif test_scenario == "apply_auto":
                orchestrator.run_apply_auto()
            elif test_scenario == "apply_review":
                orchestrator.run_apply_review()
            else:
                raise ValueError(f"Unknown test scenario: {test_scenario}")
            
            checkpoint = context.get_checkpoint()
            result["success"] = True
            result["files_updated"] = len(checkpoint.get("updated_files", []))
            result["files_failed"] = len(checkpoint.get("failed_files", []))
            result["patterns_applied"] = len(checkpoint.get("patterns_applied", []))
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        result["duration"] = time.time() - start_time
        return result
    
    def cleanup(self):
        """Clean up cloned repository."""
        if self.repo_path and self.repo_path.exists():
            shutil.rmtree(self.repo_path)
            self.cloned = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.cleanup()


class RepositoryTestRunner:
    """
    Runner for executing multiple repository tests in parallel.
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize test runner.
        
        Args:
            max_workers: Maximum number of parallel workers
        """
        self.max_workers = max_workers
        self.results: List[Dict[str, Any]] = []
    
    def run_repository_tests(
        self,
        repo_url: str,
        scenarios: List[str],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Run multiple test scenarios for a repository.
        
        Args:
            repo_url: Repository URL
            scenarios: List of scenario names to run
            **kwargs: Additional arguments for tests
        
        Returns:
            List of test results
        """
        tester = RepositoryTester(repo_url)
        results = []
        
        try:
            tester.clone_repository()
            
            for scenario in scenarios:
                result = tester.run_migration_test(scenario, **kwargs)
                results.append(result)
        finally:
            tester.cleanup()
        
        self.results.extend(results)
        return results
    
    def run_multiple_repositories(
        self,
        repos: List[Dict[str, Any]],
        scenarios: List[str],
        **kwargs
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run tests for multiple repositories (can be parallelized).
        
        Args:
            repos: List of repository dictionaries with 'url' key
            scenarios: List of scenario names to run
            **kwargs: Additional arguments for tests
        
        Returns:
            Dictionary mapping repo URLs to test results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        all_results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_repo = {
                executor.submit(
                    self.run_repository_tests,
                    repo["url"],
                    scenarios,
                    **kwargs
                ): repo["url"]
                for repo in repos
            }
            
            for future in as_completed(future_to_repo):
                repo_url = future_to_repo[future]
                try:
                    results = future.result()
                    all_results[repo_url] = results
                except Exception as e:
                    all_results[repo_url] = [{
                        "scenario": "setup",
                        "success": False,
                        "error": str(e)
                    }]
        
        return all_results
    
    def generate_report(self, output_path: Path):
        """Generate test report."""
        report = {
            "timestamp": time.time(),
            "total_repos": len(set(r.get("repo_url") for r in self.results)),
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.get("success")),
            "failed": sum(1 for r in self.results if not r.get("success")),
            "results": self.results
        }
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

