"""
Test Writer Agent - Test generation with codebase discovery
"""

from migratex.agents import BaseAgent
from pathlib import Path
from typing import List, Dict, Any


class TestWriterAgent(BaseAgent):
    """
    Designs and adapts tests to validate migrations.
    Ensures behaviour is preserved across the migration.
    """
    
    def run(self):
        """Generate tests for migrated code."""
        # Discover test codebases
        test_codebases = self.discover_test_codebases()
        
        # Extract test patterns from codebases
        test_patterns = self.extract_test_patterns(test_codebases)
        
        # Generate test files
        self.generate_test_files(test_patterns)
    
    def discover_test_codebases(self) -> List[Path]:
        """
        Discover SK/AutoGen codebases for testing.
        Uses QA/Validation agent's discovery mechanism.
        """
        from migratex.agents.qa_validation import QAValidationAgent
        
        qa_agent = QAValidationAgent(self.context)
        repos = qa_agent.discover_repositories()
        codebase_paths = qa_agent.clone_repositories(repos)
        
        return codebase_paths
    
    def extract_test_patterns(self, codebase_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Extract test patterns from real codebases.
        Identifies how SK/AutoGen code is tested.
        """
        test_patterns = []
        
        for codebase_path in codebase_paths:
            # Find test files
            test_files = list(codebase_path.rglob("test_*.py")) + list(codebase_path.rglob("*_test.py"))
            
            for test_file in test_files:
                pattern = {
                    "source_file": str(test_file),
                    "test_type": self._classify_test(test_file),
                    "framework_patterns": self._extract_framework_patterns(test_file)
                }
                test_patterns.append(pattern)
        
        return test_patterns
    
    def _classify_test(self, test_file: Path) -> str:
        """Classify test type (unit, integration, e2e)."""
        content = test_file.read_text()
        
        if "integration" in content.lower() or "e2e" in content.lower():
            return "integration"
        elif "end-to-end" in content.lower():
            return "e2e"
        else:
            return "unit"
    
    def _extract_framework_patterns(self, test_file: Path) -> List[str]:
        """Extract SK/AutoGen framework usage patterns from test."""
        content = test_file.read_text()
        patterns = []
        
        # Look for common SK/AutoGen imports and usage
        if "semantic_kernel" in content or "sk." in content:
            patterns.append("semantic_kernel")
        if "autogen" in content:
            patterns.append("autogen")
        
        return patterns
    
    def generate_test_files(self, test_patterns: List[Dict[str, Any]]):
        """Generate test files based on extracted patterns."""
        tests_dir = Path("tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Generate unit tests
        unit_tests_dir = tests_dir / "unit"
        unit_tests_dir.mkdir(exist_ok=True)
        
        # Generate integration tests
        integration_tests_dir = tests_dir / "integration"
        integration_tests_dir.mkdir(exist_ok=True)
        
        # TODO: Generate actual test files based on patterns
        # This would create pytest test files that validate migrations
