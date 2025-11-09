"""
Unit tests for pattern definitions and transformation logic
"""

import pytest
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from migratex.languages.python.patterns import PythonPatterns
from migratex.patterns.library import PatternLibrary
from migratex.agents.refactorer import RefactorerAgent
from migratex.agents.codemod_designer import CodemodDesignerAgent
from migratex.core.context import MigrationContext


class TestPythonPatterns:
    """Test Python pattern definitions."""
    
    def test_patterns_loaded(self):
        """Test that patterns are loaded correctly."""
        patterns = PythonPatterns.get_patterns()
        assert len(patterns) > 0
        assert isinstance(patterns, dict) and len(patterns) > 0, "Patterns should be non-empty dict"
    
    def test_sk_import_patterns(self):
        """Test Semantic Kernel import patterns."""
        patterns = PythonPatterns.get_patterns()
        
        # Check SK_IMPORT_KERNEL pattern
        sk_kernel = patterns.get("sk_import_kernel")
        assert sk_kernel is not None
        assert sk_kernel["id"] == "SK_IMPORT_KERNEL"
        assert sk_kernel["confidence"] == "high"
        assert sk_kernel["type"] == "import"
        assert sk_kernel["framework"] == "semantic_kernel"
        
        # Check pattern regex matches expected import
        pattern_regex = sk_kernel["pattern"]
        test_code = "from semantic_kernel import Kernel"
        assert re.search(pattern_regex, test_code) is not None
    
    def test_autogen_import_patterns(self):
        """Test AutoGen import patterns."""
        patterns = PythonPatterns.get_patterns()
        
        # Check AUTOGEN_IMPORT_CONVERSABLE pattern
        autogen_conversable = patterns.get("autogen_import_conversable")
        assert autogen_conversable is not None
        assert autogen_conversable["id"] == "AUTOGEN_IMPORT_CONVERSABLE"
        assert autogen_conversable["confidence"] == "high"
        assert autogen_conversable["type"] == "import"
        assert autogen_conversable["framework"] == "autogen"
        
        # Check pattern regex matches expected import
        pattern_regex = autogen_conversable["pattern"]
        test_code = "from autogen import ConversableAgent"
        assert re.search(pattern_regex, test_code) is not None
    
    def test_instantiation_patterns(self):
        """Test instantiation patterns."""
        patterns = PythonPatterns.get_patterns()
        
        # Check SK_KERNEL_INSTANTIATION
        sk_kernel_inst = patterns.get("sk_kernel_instantiation")
        assert sk_kernel_inst is not None
        assert sk_kernel_inst["type"] == "instantiation"
        
        # Check pattern matches Kernel()
        pattern_regex = sk_kernel_inst["pattern"]
        test_code = "kernel = Kernel()"
        assert re.search(pattern_regex, test_code) is not None
    
    def test_decorator_patterns(self):
        """Test decorator patterns."""
        patterns = PythonPatterns.get_patterns()
        
        # Check SK_DECORATOR_KERNEL_FUNCTION
        sk_decorator = patterns.get("sk_decorator_kernel_function")
        assert sk_decorator is not None
        assert sk_decorator["type"] == "decorator"
        
        # Check pattern matches @kernel_function
        pattern_regex = sk_decorator["pattern"]
        test_code = "@kernel_function\ndef my_function():"
        assert re.search(pattern_regex, test_code) is not None
    
    def test_class_inheritance_patterns(self):
        """Test class inheritance patterns."""
        patterns = PythonPatterns.get_patterns()
        
        # Check SK_CLASS_INHERITANCE_KERNEL_AGENT
        sk_class = patterns.get("sk_class_inheritance_kernel_agent")
        assert sk_class is not None
        assert sk_class["type"] == "class_inheritance"
        
        # Check pattern matches class definition
        pattern_regex = sk_class["pattern"]
        test_code = "class MyAgent(KernelAgent):"
        assert re.search(pattern_regex, test_code) is not None
    
    def test_all_patterns_have_required_fields(self):
        """Test that all patterns have required fields."""
        patterns = PythonPatterns.get_patterns()
        
        required_fields = ["id", "pattern", "replacement", "confidence", "type"]
        
        for pattern_key, pattern_def in patterns.items():
            for field in required_fields:
                assert field in pattern_def, f"Pattern {pattern_key} missing field {field}"


class TestPatternLibrary:
    """Test PatternLibrary integration."""
    
    def test_library_loads_patterns(self):
        """Test that PatternLibrary loads patterns from PythonPatterns."""
        library = PatternLibrary()
        patterns = library.get_all_patterns()
        
        assert len(patterns) > 0
        
        # Check that SK_IMPORT_KERNEL is loaded
        sk_kernel = library.get_pattern("SK_IMPORT_KERNEL")
        assert sk_kernel is not None
        assert sk_kernel["id"] == "SK_IMPORT_KERNEL"
        assert "pattern" in sk_kernel  # Should have regex pattern
        assert "replacement" in sk_kernel  # Should have replacement
    
    def test_library_high_confidence_check(self):
        """Test high confidence pattern checking."""
        library = PatternLibrary()
        
        # SK_IMPORT_KERNEL should be high confidence
        assert library.is_high_confidence("SK_IMPORT_KERNEL") is True
        
        # Non-existent pattern should return False
        assert library.is_high_confidence("NON_EXISTENT") is False
    
    def test_library_loads_relevant_patterns(self):
        """Test loading only relevant patterns."""
        library = PatternLibrary()
        
        pattern_ids = ["SK_IMPORT_KERNEL", "AUTOGEN_IMPORT_CONVERSABLE"]
        relevant = library.load_relevant(pattern_ids)
        
        assert len(relevant) == 2
        assert "SK_IMPORT_KERNEL" in relevant
        assert "AUTOGEN_IMPORT_CONVERSABLE" in relevant


class TestRefactorerAgent:
    """Test RefactorerAgent transformation logic."""
    
    def test_refactorer_initialization(self):
        """Test RefactorerAgent initializes correctly."""
        with TemporaryDirectory() as tmpdir:
            context = MigrationContext(project_path=Path(tmpdir), mode="auto")
            refactorer = RefactorerAgent(context)
            
            assert refactorer.context == context
            assert refactorer.parser is not None
            assert isinstance(refactorer.decision_cache, dict)
    
    def test_transform_file_import_replacement(self):
        """Test file transformation with import replacement."""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            context = MigrationContext(project_path=project_path, mode="auto")
            
            # Create test file with SK import
            test_file = project_path / "test.py"
            test_file.write_text("from semantic_kernel import Kernel\nkernel = Kernel()\n")
            
            # Set up context with patterns
            context.report = {
                "patterns": [
                    {
                        "id": "SK_IMPORT_KERNEL",
                        "file": str(test_file),
                        "confidence": "high",
                        "source": "rule"
                    }
                ]
            }
            
            refactorer = RefactorerAgent(context)
            
            # Transform file
            result = refactorer._transform_file(test_file, context.report["patterns"], auto_mode=True)
            
            assert result is True
            
            # Check transformation was applied
            transformed_content = test_file.read_text()
            assert "from microsoft.agentframework import AgentFrameworkClient" in transformed_content
            assert "from semantic_kernel import Kernel" not in transformed_content
    
    def test_transform_file_skips_low_confidence_in_auto_mode(self):
        """Test that low-confidence patterns are skipped in auto mode."""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            context = MigrationContext(project_path=project_path, mode="auto")
            
            # Create test file
            test_file = project_path / "test.py"
            test_file.write_text("from semantic_kernel import Kernel\n")
            
            # Set up context with low-confidence pattern
            context.report = {
                "patterns": [
                    {
                        "id": "SK_IMPORT_KERNEL_BUILDER",  # Medium confidence
                        "file": str(test_file),
                        "confidence": "medium",
                        "source": "rule"
                    }
                ]
            }
            
            refactorer = RefactorerAgent(context)
            
            # Transform file (should skip medium confidence in auto mode)
            result = refactorer._transform_file(test_file, context.report["patterns"], auto_mode=True)
            
            # Should not transform (medium confidence skipped in auto mode)
            assert result is False


class TestCodemodDesignerAgent:
    """Test CodemodDesignerAgent."""
    
    def test_codemod_designer_initialization(self):
        """Test CodemodDesignerAgent initializes correctly."""
        with TemporaryDirectory() as tmpdir:
            context = MigrationContext(project_path=Path(tmpdir), mode="analyze")
            designer = CodemodDesignerAgent(context)
            
            assert designer.context == context
    
    def test_codemod_designer_prepares_codemods(self):
        """Test that CodemodDesignerAgent prepares codemods correctly."""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            context = MigrationContext(project_path=project_path, mode="analyze")
            
            # Set up context with detected patterns
            context.report = {
                "patterns": [
                    {
                        "id": "SK_IMPORT_KERNEL",
                        "confidence": "high",
                        "source": "rule"
                    },
                    {
                        "id": "AUTOGEN_IMPORT_CONVERSABLE",
                        "confidence": "high",
                        "source": "rule"
                    }
                ]
            }
            
            designer = CodemodDesignerAgent(context)
            designer.run()
            
            # Check codemods were created
            assert hasattr(context, "codemods")
            assert len(context.codemods) > 0
            
            # Check codemod structure
            codemod = context.codemods.get("SK_IMPORT_KERNEL")
            assert codemod is not None
            assert "pattern_id" in codemod
            assert "transformer" in codemod
            assert "pattern_def" in codemod
    
    def test_codemod_designer_handles_no_patterns(self):
        """Test CodemodDesignerAgent handles case with no patterns."""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            context = MigrationContext(project_path=project_path, mode="analyze")
            
            # Set up context with no patterns
            context.report = {}
            
            designer = CodemodDesignerAgent(context)
            designer.run()
            
            # Should complete without error
            assert True  # If we get here, no exception was raised

