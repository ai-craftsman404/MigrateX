"""
Parallel Testing Agents - Run tests in parallel using multiple agents
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing
import json
from migratex.testing.results_tracker import TestingResultsTracker


class ParallelTestAgent:
    """
    Individual test agent that runs a subset of tests in parallel.
    Each agent handles a specific test category or test file.
    """
    
    def __init__(self, agent_id: str, test_paths: List[Path], tracker: TestingResultsTracker):
        self.agent_id = agent_id
        self.test_paths = test_paths
        self.tracker = tracker
        self.results: Dict[str, Any] = {}
    
    def run_tests(self) -> Dict[str, Any]:
        """Run assigned tests and return results."""
        import subprocess
        import sys
        
        # Run pytest on assigned test paths
        pytest_args = [
            sys.executable, "-m", "pytest",
            *[str(p) for p in self.test_paths],
            "-v",
            "--tb=short",
            "--junit-xml", f"test-results-{self.agent_id}.xml",
            "--cov=migratex",
            "--cov-report=json",
            "--cov-report=term",
        ]
        
        try:
            result = subprocess.run(
                pytest_args,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per agent
            )
            
            self.results = {
                "agent_id": self.agent_id,
                "test_paths": [str(p) for p in self.test_paths],
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests_run": self._parse_test_count(result.stdout),
                "tests_passed": self._parse_passed_count(result.stdout),
                "tests_failed": self._parse_failed_count(result.stdout),
                "status": "completed" if result.returncode == 0 else "failed"
            }
            
            # Record results in tracker
            self.tracker.record_unit_test_result(
                f"parallel_agent_{self.agent_id}",
                self.results["tests_passed"],
                self.results["tests_failed"],
                self.results["tests_run"]
            )
            
        except subprocess.TimeoutExpired:
            self.results = {
                "agent_id": self.agent_id,
                "status": "timeout",
                "error": "Test execution exceeded timeout"
            }
        except Exception as e:
            self.results = {
                "agent_id": self.agent_id,
                "status": "error",
                "error": str(e)
            }
        
        return self.results
    
    def _parse_test_count(self, output: str) -> int:
        """Parse total test count from pytest output."""
        import re
        match = re.search(r'(\d+)\s+passed', output)
        return int(match.group(1)) if match else 0
    
    def _parse_passed_count(self, output: str) -> int:
        """Parse passed test count from pytest output."""
        import re
        match = re.search(r'(\d+)\s+passed', output)
        return int(match.group(1)) if match else 0
    
    def _parse_failed_count(self, output: str) -> int:
        """Parse failed test count from pytest output."""
        import re
        match = re.search(r'(\d+)\s+failed', output)
        return int(match.group(1)) if match else 0


class ParallelTestOrchestrator:
    """
    Orchestrates multiple testing agents to run tests in parallel.
    Distributes test files across agents for maximum parallelization.
    """
    
    def __init__(
        self,
        test_dir: Path,
        num_agents: Optional[int] = None,
        execution_mode: str = "process"
    ):
        self.test_dir = test_dir
        self.num_agents = num_agents or min(multiprocessing.cpu_count(), 8)
        self.execution_mode = execution_mode  # "process" or "thread"
        self.tracker = TestingResultsTracker()
        self.agents: List[ParallelTestAgent] = []
        self.results: List[Dict[str, Any]] = []
    
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in test directory."""
        test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(self.test_dir.rglob(pattern))
        return sorted(test_files)
    
    def distribute_tests(self, test_files: List[Path]) -> Dict[str, List[Path]]:
        """
        Distribute test files across agents.
        Groups by category for better parallelization.
        """
        distribution: Dict[str, List[Path]] = {}
        
        # Group tests by category
        unit_tests = [f for f in test_files if "unit" in str(f)]
        integration_tests = [f for f in test_files if "integration" in str(f)]
        e2e_tests = [f for f in test_files if "e2e" in str(f)]
        edge_case_tests = [f for f in test_files if "edge_case" in str(f)]
        outlier_tests = [f for f in test_files if "outlier" in str(f)]
        performance_tests = [f for f in test_files if "performance" in str(f)]
        
        # Distribute unit tests across multiple agents
        unit_per_agent = max(1, len(unit_tests) // (self.num_agents - 2))
        for i in range(min(self.num_agents - 2, len(unit_tests))):
            start = i * unit_per_agent
            end = start + unit_per_agent if i < self.num_agents - 3 else len(unit_tests)
            distribution[f"unit_agent_{i}"] = unit_tests[start:end]
        
        # Dedicated agents for other categories
        if integration_tests:
            distribution["integration_agent"] = integration_tests
        if e2e_tests:
            distribution["e2e_agent"] = e2e_tests
        if edge_case_tests:
            distribution["edge_case_agent"] = edge_case_tests
        if outlier_tests:
            distribution["outlier_agent"] = outlier_tests
        if performance_tests:
            distribution["performance_agent"] = performance_tests
        
        return distribution
    
    def create_agents(self, distribution: Dict[str, List[Path]]):
        """Create testing agents for each test group."""
        self.agents = [
            ParallelTestAgent(agent_id, test_paths, self.tracker)
            for agent_id, test_paths in distribution.items()
            if test_paths  # Only create agents with tests
        ]
    
    def run_parallel(self) -> Dict[str, Any]:
        """Run all test agents in parallel."""
        # Discover and distribute tests
        test_files = self.discover_test_files()
        distribution = self.distribute_tests(test_files)
        self.create_agents(distribution)
        
        if not self.agents:
            return {
                "status": "no_tests",
                "message": "No test files found"
            }
        
        # Start task tracking
        for agent in self.agents:
            self.tracker.start_task(
                f"parallel_agent_{agent.agent_id}",
                f"Parallel Test Agent {agent.agent_id}",
                f"Run tests: {', '.join(str(p.name) for p in agent.test_paths[:3])}..."
            )
        
        # Execute agents in parallel
        if self.execution_mode == "process":
            executor = ProcessPoolExecutor(max_workers=self.num_agents)
        else:
            executor = ThreadPoolExecutor(max_workers=self.num_agents)
        
        results = []
        with executor:
            future_to_agent = {
                executor.submit(agent.run_tests): agent
                for agent in self.agents
            }
            
            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Complete task
                    self.tracker.complete_task(
                        f"parallel_agent_{agent.agent_id}",
                        result.get("status") == "completed"
                    )
                except Exception as e:
                    results.append({
                        "agent_id": agent.agent_id,
                        "status": "error",
                        "error": str(e)
                    })
                    self.tracker.complete_task(
                        f"parallel_agent_{agent.agent_id}",
                        False
                    )
        
        self.results = results
        
        # Generate summary
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate summary of parallel test execution."""
        total_tests = sum(r.get("tests_run", 0) for r in self.results)
        total_passed = sum(r.get("tests_passed", 0) for r in self.results)
        total_failed = sum(r.get("tests_failed", 0) for r in self.results)
        completed_agents = sum(1 for r in self.results if r.get("status") == "completed")
        failed_agents = sum(1 for r in self.results if r.get("status") == "failed")
        
        summary = {
            "execution_mode": self.execution_mode,
            "num_agents": len(self.agents),
            "total_tests_run": total_tests,
            "total_tests_passed": total_passed,
            "total_tests_failed": total_failed,
            "agents_completed": completed_agents,
            "agents_failed": failed_agents,
            "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "agent_results": self.results,
            "overall_status": "passed" if total_failed == 0 and failed_agents == 0 else "failed"
        }
        
        return summary
    
    def save_results(self, output_path: Path):
        """Save parallel test results to file."""
        summary = self.generate_summary()
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)


class SpecializedTestAgent:
    """
    Specialized testing agent for specific test categories.
    Can be run independently or as part of parallel execution.
    """
    
    def __init__(self, category: str, test_paths: List[Path], tracker: TestingResultsTracker):
        self.category = category
        self.test_paths = test_paths
        self.tracker = tracker
        self.agent = ParallelTestAgent(f"{category}_specialized", test_paths, tracker)
    
    def run(self) -> Dict[str, Any]:
        """Run specialized test category."""
        return self.agent.run_tests()


class TestAgentFactory:
    """Factory for creating specialized test agents."""
    
    @staticmethod
    def create_unit_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for unit tests."""
        unit_tests = list(test_dir.rglob("unit/**/test_*.py"))
        return SpecializedTestAgent("unit", unit_tests, tracker)
    
    @staticmethod
    def create_integration_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for integration tests."""
        integration_tests = list(test_dir.rglob("integration/**/test_*.py"))
        return SpecializedTestAgent("integration", integration_tests, tracker)
    
    @staticmethod
    def create_e2e_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for E2E tests."""
        e2e_tests = list(test_dir.rglob("e2e/**/test_*.py"))
        return SpecializedTestAgent("e2e", e2e_tests, tracker)
    
    @staticmethod
    def create_edge_case_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for edge case tests."""
        edge_case_tests = list(test_dir.rglob("**/test_edge*.py"))
        return SpecializedTestAgent("edge_case", edge_case_tests, tracker)
    
    @staticmethod
    def create_outlier_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for outlier tests."""
        outlier_tests = list(test_dir.rglob("**/test_outlier*.py"))
        return SpecializedTestAgent("outlier", outlier_tests, tracker)
    
    @staticmethod
    def create_performance_test_agent(test_dir: Path, tracker: TestingResultsTracker) -> SpecializedTestAgent:
        """Create agent for performance tests."""
        performance_tests = list(test_dir.rglob("performance/**/test_*.py"))
        return SpecializedTestAgent("performance", performance_tests, tracker)

