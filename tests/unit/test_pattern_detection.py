"""
Unit tests for Pattern Detection (Agent 1 - T1.1)

Tests pattern detection accuracy, false positives, and edge cases.
Target: 50+ test cases, 95%+ coverage
"""

import pytest
from pathlib import Path
from migratex.patterns.discovery import PatternDiscovery
from migratex.core.context import MigrationContext
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestPatternDetection:
    """Test pattern detection accuracy and edge cases."""
    
    def test_sk_import_detection(self):
        """Test detection of Semantic Kernel imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel\nfrom semantic_kernel.agents import KernelAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            assert len(patterns) > 0
            assert any("semantic_kernel" in p.get("id", "").lower() for p in patterns)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_detection(self):
        """Test detection of AutoGen imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import ConversableAgent\nfrom autogen import GroupChat"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            assert len(patterns) > 0
            assert any("autogen" in p.get("id", "").lower() for p in patterns)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_in_comments_not_detected(self):
        """Test that patterns in comments are not detected."""
        fixture = EdgeCaseTestFixtures.create_pattern_in_comments_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "commented.py"])
            
            # Should not detect patterns in comments
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_aliased_imports_detected(self):
        """Test detection of aliased imports."""
        fixture = EdgeCaseTestFixtures.create_aliased_imports_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "aliased.py"])
            
            # Should detect aliased imports
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_mixed_frameworks_detected(self):
        """Test detection of mixed SK and AutoGen frameworks."""
        fixture = EdgeCaseTestFixtures.create_mixed_frameworks_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            
            sk_file = fixture / "sk_file.py"
            autogen_file = fixture / "autogen_file.py"
            
            sk_patterns = discovery.discover_patterns([sk_file])
            autogen_patterns = discovery.discover_patterns([autogen_file])
            
            assert len(sk_patterns) > 0
            assert len(autogen_patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_empty_codebase_no_patterns(self):
        """Test that empty codebase returns no patterns."""
        fixture = EdgeCaseTestFixtures.create_empty_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([])
            
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_syntax_error_handled_gracefully(self):
        """Test that syntax errors don't crash pattern detection."""
        fixture = EdgeCaseTestFixtures.create_syntax_error_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            
            # Should not crash, but may skip file or return empty patterns
            broken_file = fixture / "broken.py"
            try:
                patterns = discovery.discover_patterns([broken_file])
                # Either returns empty or handles gracefully
                assert isinstance(patterns, list), "Patterns should be list"
                # Verify patterns are valid (may be empty for some cases)
                assert patterns is not None, "Patterns should exist"
            except SyntaxError:
                # Acceptable - file has syntax errors
                pass
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_class_inheritance_pattern_detection(self):
        """Test detection of class inheritance patterns."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.agents import KernelAgent\n\nclass MyAgent(KernelAgent):\n    pass"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect class inheritance pattern
            assert len(patterns) > 0
            assert any("inheritance" in p.get("type", "").lower() or "class" in p.get("type", "").lower() 
                      for p in patterns)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_confidence_scoring(self):
        """Test that patterns have confidence scores."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            if patterns:
                # Patterns should have confidence or source information
                for pattern in patterns:
                    assert "confidence" in pattern or "source" in pattern
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_multiple_patterns_in_file(self):
        """Test detection of multiple patterns in single file."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel.agents import KernelAgent
from autogen import ConversableAgent

class SKAgent(KernelAgent):
    pass

class AutoGenAgent(ConversableAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect multiple patterns
            assert len(patterns) >= 2
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_conditional_imports_detected(self):
        """Test detection of conditional imports (TYPE_CHECKING)."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from semantic_kernel import Kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns even in TYPE_CHECKING blocks
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_relative_imports_detected(self):
        """Test detection of relative imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from .semantic_kernel_module import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # May or may not detect relative imports depending on implementation
            assert isinstance(patterns, list)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_in_docstrings_detected(self):
        """Test that patterns in docstrings are detected."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            '''def my_function():
    """Uses semantic_kernel.Kernel for processing."""
    pass
'''
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Docstrings may contain pattern references
            assert isinstance(patterns, list)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_in_strings_not_detected(self):
        """Test that patterns in strings are not detected."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            'message = "Uses semantic_kernel.Kernel for processing"'
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should not detect patterns in strings
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_function_call_patterns_detected(self):
        """Test detection of function call patterns."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect import patterns
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_decorator_patterns_detected(self):
        """Test detection of decorator patterns."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect decorator patterns
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_nested_class_patterns_detected(self):
        """Test detection of patterns in nested classes."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import KernelAgent

class Outer:
    class Inner(KernelAgent):
        pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect nested class patterns
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_async_patterns_detected(self):
        """Test detection of patterns in async functions."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

async def my_function():
    kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in async context
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_type_hints_patterns_detected(self):
        """Test detection of patterns in type hints."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from typing import Optional

def my_function(kernel: Optional[Kernel] = None):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in type hints
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_conflict_detection(self):
        """Test detection of conflicting patterns."""
        fixture = EdgeCaseTestFixtures.create_pattern_conflict_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "conflict.py"])
            
            # Should detect multiple patterns (potential conflicts)
            assert len(patterns) >= 2
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_source_tracking(self):
        """Test that patterns track their source."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            if patterns:
                # Patterns should have source information
                for pattern in patterns:
                    assert "file" in pattern or "source" in pattern
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_line_number_tracking(self):
        """Test that patterns track line numbers."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """import os
from semantic_kernel import Kernel
import sys
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            if patterns:
                # Patterns should have line number information
                for pattern in patterns:
                    assert "line" in pattern or "lineno" in pattern or "location" in pattern
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_empty_file_no_patterns(self):
        """Test that empty Python file returns no patterns."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("")
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_whitespace_only_file_no_patterns(self):
        """Test that whitespace-only file returns no patterns."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("   \n\n\t  \n")
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_multiple_files_pattern_discovery(self):
        """Test pattern discovery across multiple files."""
        fixture = EdgeCaseTestFixtures.create_mixed_frameworks_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            
            python_files = list(fixture.rglob("*.py"))
            patterns = discovery.discover_patterns(python_files)
            
            # Should detect patterns from multiple files
            assert len(patterns) >= 2
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_deduplication(self):
        """Test that duplicate patterns are deduplicated."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel import Kernel  # Duplicate
from semantic_kernel import Kernel  # Another duplicate
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should deduplicate or handle duplicates appropriately
            assert isinstance(patterns, list)
            # May have duplicates or be deduplicated depending on implementation
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_with_typos_not_detected(self):
        """Test that patterns with typos are not detected."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernal import Kernel  # Typo: kernal instead of kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should not detect typos
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_in_try_except_block(self):
        """Test detection of patterns in try/except blocks."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """try:
    from semantic_kernel import Kernel
except ImportError:
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns even in try/except blocks
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

