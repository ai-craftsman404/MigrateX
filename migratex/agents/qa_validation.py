"""
QA/Validation Agent - Rigorous testing against real SK/AutoGen codebases
"""

from migratex.agents import BaseAgent
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import json
from migratex.testing.test_suite_executor import TestSuiteExecutor


class QAValidationAgent(BaseAgent):
    """
    Rigorous testing agent that validates migrations against real-world codebases.
    Discovers, clones, and tests against real SK/AutoGen repositories.
    Implements comprehensive test suite plan with standard tasks T1-T6.
    """
    
    def __init__(self, context):
        super().__init__(context)
        self.test_codebases_dir = Path("test_codebases")
        self.test_codebases_dir.mkdir(exist_ok=True)
    
    def run(self):
        """Run comprehensive validation against real codebases."""
        # Discover SK/AutoGen repositories
        repos = self.discover_repositories()
        
        # Filter by priority if needed
        if self.context.verbose:
            repos = [r for r in repos if r.get("priority") == "first_pass"]
        
        # Clone/download test codebases
        cloned_repos = self.clone_repositories(repos)
        
        # Execute standard test tasks for each repo
        all_results = []
        for repo_info, repo_path in zip(repos, cloned_repos):
            executor = TestSuiteExecutor(repo_path, repo_info)
            results = executor.execute_all_tasks()
            all_results.append(results)
        
        # Generate validation report
        self.generate_validation_report(all_results)
    
    def discover_repositories(self) -> List[Dict[str, str]]:
        """
        Discover SK/AutoGen repositories from GitHub.
        Returns list of repository metadata.
        Based on comprehensive test suite plan with Tier 1, 2, 3 repositories.
        """
        repositories = [
            # Tier 1 — Canonical Framework Repos
            {
                "name": "microsoft/semantic-kernel",
                "url": "https://github.com/microsoft/semantic-kernel.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 1,
                "description": "Core SDK - Multi-language (C#, Python, Java). Contains SDK + embedded samples.",
                "priority": "first_pass"
            },
            {
                "name": "microsoft/autogen",
                "url": "https://github.com/microsoft/autogen.git",
                "type": "autogen",
                "language": "python",
                "tier": 1,
                "description": "Core Framework - Primary reference for AutoGen patterns",
                "priority": "first_pass"
            },
            # Tier 2 — Semantic Kernel Application Repos
            {
                "name": "Azure-Samples/semantic-kernel-advanced-usage",
                "url": "https://github.com/Azure-Samples/semantic-kernel-advanced-usage.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Enterprise-like usage. Orchestration, hosting, telemetry.",
                "priority": "first_pass"
            },
            {
                "name": "Azure-Samples/semantic-kernel-workshop",
                "url": "https://github.com/Azure-Samples/semantic-kernel-workshop.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Tutorial-style, multiple small scenarios. Good for incremental tests.",
                "priority": "second_pass"
            },
            {
                "name": "microsoft/semantic-kernel-starters",
                "url": "https://github.com/microsoft/semantic-kernel-starters.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Self-contained starter projects in .NET, Python, Java.",
                "priority": "third_pass"
            },
            {
                "name": "rvinothrajendran/MicrosoftSemanticKernelSamples",
                "url": "https://github.com/rvinothrajendran/MicrosoftSemanticKernelSamples.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Community project, real-world structure. Good for robustness testing.",
                "priority": "third_pass"
            },
            # Tier 3 — Mixed / Multi-Agent / Full Apps
            {
                "name": "Azure-Samples/agentic-aiops-semantic-kernel",
                "url": "https://github.com/Azure-Samples/agentic-aiops-semantic-kernel.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 3,
                "description": "Multi-agent AIOps system using Semantic Kernel and orchestration patterns.",
                "priority": "second_pass"
            },
            {
                "name": "Azure-Samples/multi-agent-workshop",
                "url": "https://github.com/Azure-Samples/multi-agent-workshop.git",
                "type": "mixed",
                "language": "python",
                "tier": 3,
                "description": "Multi-agent scenarios using various frameworks. Great for mixed framework detection.",
                "priority": "third_pass"
            },
            {
                "name": "Azure-Samples/dream-team",
                "url": "https://github.com/Azure-Samples/dream-team.git",
                "type": "autogen",
                "language": "python",
                "tier": 3,
                "description": "Full multi-agent AutoGen app with backend + React UI.",
                "priority": "second_pass"
            },
            # Production-Level Repositories (Added from search)
            {
                "name": "microsoft/chat-copilot",
                "url": "https://github.com/microsoft/chat-copilot.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 3,
                "description": "Full-stack web application (React + backend) showing SK in production web apps.",
                "priority": "first_pass"
            },
            {
                "name": "Azure/semantic-kernel-bot-in-a-box",
                "url": "https://github.com/Azure/semantic-kernel-bot-in-a-box.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 3,
                "description": "Enterprise bot template with Azure deployment and extensible architecture.",
                "priority": "first_pass"
            },
            {
                "name": "Azure/plan-search-chatbot",
                "url": "https://github.com/Azure/plan-search-chatbot.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 3,
                "description": "Production chatbot incorporating Semantic Kernel for intelligent planning.",
                "priority": "first_pass"
            },
            {
                "name": "Azure-Samples/app-service-agentic-semantic-kernel-ai-foundry-agent",
                "url": "https://github.com/Azure-Samples/app-service-agentic-semantic-kernel-ai-foundry-agent.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 3,
                "description": "Agentic web app with SK + Foundry, production-level architecture.",
                "priority": "first_pass"
            },
            {
                "name": "victordibia/designing-multiagent-systems",
                "url": "https://github.com/victordibia/designing-multiagent-systems.git",
                "type": "autogen",
                "language": "python",
                "tier": 3,
                "description": "Production multi-agent patterns from published book with real-world implementations.",
                "priority": "first_pass"
            },
            {
                "name": "jkmaina/autogen_blueprint",
                "url": "https://github.com/jkmaina/autogen_blueprint.git",
                "type": "autogen",
                "language": "python",
                "tier": 3,
                "description": "Complete guide to building multi-agent AI systems with AutoGen, production patterns.",
                "priority": "first_pass"
            },
            {
                "name": "PacktPublishing/Mastering-Multi-Agent-Development-with-AutoGen",
                "url": "https://github.com/PacktPublishing/Mastering-Multi-Agent-Development-with-AutoGen.git",
                "type": "autogen",
                "language": "python",
                "tier": 3,
                "description": "Advanced patterns and near-production examples from published book.",
                "priority": "second_pass"
            },
            {
                "name": "Azure-Samples/semantic-kernel-rag-chat",
                "url": "https://github.com/Azure-Samples/semantic-kernel-rag-chat.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Enterprise chat implementation with RAG patterns using Semantic Kernel.",
                "priority": "second_pass"
            },
            {
                "name": "DavidGSola/pychatbot-semantic-kernel",
                "url": "https://github.com/DavidGSola/pychatbot-semantic-kernel.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Chatbot with extensible plugin architecture, community project.",
                "priority": "second_pass"
            },
            {
                "name": "30DaysOf/semantic-kernel",
                "url": "https://github.com/30DaysOf/semantic-kernel.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Learning project with practical real-world application demonstrating SK capabilities.",
                "priority": "third_pass"
            },
            {
                "name": "GregorBiswanger/SemanticFlow",
                "url": "https://github.com/GregorBiswanger/SemanticFlow.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Workflow framework simplifying real-world AI tasks with Semantic Kernel.",
                "priority": "third_pass"
            },
            {
                "name": "PacktPublishing/Building-AI-Applications-with-Microsoft-Semantic-Kernel",
                "url": "https://github.com/PacktPublishing/Building-AI-Applications-with-Microsoft-Semantic-Kernel.git",
                "type": "semantic_kernel",
                "language": "python",
                "tier": 2,
                "description": "Comprehensive examples from published book covering various production patterns.",
                "priority": "third_pass"
            },
        ]
        
        return repositories
    
    def clone_repositories(self, repos: List[Dict[str, str]]) -> List[Path]:
        """Clone repositories to test_codebases directory."""
        cloned_paths = []
        
        for repo in repos:
            repo_name = repo["name"].split("/")[-1]
            target_path = self.test_codebases_dir / repo_name
            
            if not target_path.exists():
                try:
                    subprocess.run(
                        ["git", "clone", repo["url"], str(target_path)],
                        check=True,
                        capture_output=True
                    )
                    cloned_paths.append(target_path)
                except subprocess.CalledProcessError as e:
                    self.context.failed_files.append({
                        "file": repo["name"],
                        "error": f"Failed to clone: {e}"
                    })
            else:
                cloned_paths.append(target_path)
        
        return cloned_paths
    
    def generate_validation_report(self, results: List[Dict[str, Any]]):
        """Generate validation report from test results."""
        report_path = Path("validation-report.json")
        
        report = {
            "total_repos": len(results),
            "successful": sum(1 for r in results if all(t.get("status") in ["completed", "skipped"] for t in r.get("tasks", {}).values())),
            "failed": sum(1 for r in results if any(t.get("status") == "failed" for t in r.get("tasks", {}).values())),
            "repos": results,
            "summary": self._generate_summary(results)
        }
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        if self.context.verbose:
            print(f"Validation report saved to: {report_path}")
            print(f"Total repos tested: {len(results)}")
            print(f"Successful: {report['successful']}, Failed: {report['failed']}")
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from test results."""
        summary = {
            "total_patterns_detected": 0,
            "total_files_changed": 0,
            "repos_by_tier": {1: 0, 2: 0, 3: 0},
            "task_completion": {}
        }
        
        for result in results:
            tier = result.get("tier", 0)
            if tier in summary["repos_by_tier"]:
                summary["repos_by_tier"][tier] += 1
            
            # Count patterns detected
            t2_result = result.get("tasks", {}).get("T2", {})
            summary["total_patterns_detected"] += len(t2_result.get("patterns_detected", []))
            
            # Count files changed
            t3_result = result.get("tasks", {}).get("T3", {})
            summary["total_files_changed"] += len(t3_result.get("files_changed", []))
            
            # Track task completion
            for task_name, task_result in result.get("tasks", {}).items():
                status = task_result.get("status", "unknown")
                if task_name not in summary["task_completion"]:
                    summary["task_completion"][task_name] = {}
                summary["task_completion"][task_name][status] = summary["task_completion"][task_name].get(status, 0) + 1
        
        return summary

