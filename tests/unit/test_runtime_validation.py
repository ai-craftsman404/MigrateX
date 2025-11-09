"""
Unit tests for runtime validation module.

Tests:
- Syntax validation (valid/invalid Python)
- Import validation (valid/invalid imports)
- File-level validation
- Directory-level validation
- Error reporting
- Integration with migration workflow

Coverage target: >90%
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from migratex.validation import (
    RuntimeValidator,
    ValidationResult,
    ValidationError,
    ValidationLevel,
    validate_file,
    validate_directory,
)


class TestValidationError:
    """Test ValidationError dataclass."""
    
    def test_create_error(self):
        """Test creating validation error."""
        error = ValidationError(
            level=ValidationLevel.ERROR,
            file_path="test.py",
            line_number=10,
            column_number=5,
            error_type="SyntaxError",
            message="Invalid syntax"
        )
        
        assert error.level == ValidationLevel.ERROR
        assert error.file_path == "test.py"
        assert error.line_number == 10
        assert "SyntaxError" in str(error)
        assert "test.py:10:5" in str(error)
    
    def test_error_without_line_number(self):
        """Test error without line number."""
        error = ValidationError(
            level=ValidationLevel.WARNING,
            file_path="test.py",
            line_number=None,
            column_number=None,
            error_type="ImportWarning",
            message="Cannot resolve import"
        )
        
        assert "test.py" in str(error)
        assert "ImportWarning" in str(error)


class TestValidationResult:
    """Test ValidationResult dataclass."""
    
    def test_create_result(self):
        """Test creating validation result."""
        result = ValidationResult(
            file_path="test.py",
            is_valid=True
        )
        
        assert result.is_valid
        assert not result.has_errors
        assert not result.has_warnings
        assert len(result.errors) == 0
    
    def test_add_error_makes_invalid(self):
        """Test that adding error makes result invalid."""
        result = ValidationResult(
            file_path="test.py",
            is_valid=True
        )
        
        error = ValidationError(
            level=ValidationLevel.ERROR,
            file_path="test.py",
            line_number=10,
            column_number=5,
            error_type="SyntaxError",
            message="Invalid syntax"
        )
        
        result.add_error(error)
        
        assert not result.is_valid
        assert result.has_errors
        assert len(result.errors) == 1
        assert result.errors[0] == error
    
    def test_add_warning_keeps_valid(self):
        """Test that adding warning keeps result valid."""
        result = ValidationResult(
            file_path="test.py",
            is_valid=True
        )
        
        warning = ValidationError(
            level=ValidationLevel.WARNING,
            file_path="test.py",
            line_number=10,
            column_number=5,
            error_type="ImportWarning",
            message="Cannot resolve import"
        )
        
        result.add_error(warning)
        
        assert result.is_valid  # Still valid with warning
        assert not result.has_errors
        assert result.has_warnings
        assert len(result.warnings) == 1
    
    def test_get_all_issues(self):
        """Test getting all issues."""
        result = ValidationResult(
            file_path="test.py",
            is_valid=False
        )
        
        # Add multiple issue types
        result.add_error(ValidationError(
            level=ValidationLevel.ERROR,
            file_path="test.py",
            line_number=10,
            column_number=5,
            error_type="SyntaxError",
            message="Invalid syntax"
        ))
        
        result.add_error(ValidationError(
            level=ValidationLevel.WARNING,
            file_path="test.py",
            line_number=20,
            column_number=None,
            error_type="ImportWarning",
            message="Cannot resolve import"
        ))
        
        result.add_error(ValidationError(
            level=ValidationLevel.INFO,
            file_path="test.py",
            line_number=30,
            column_number=None,
            error_type="ImportInfo",
            message="Import may not be installed"
        ))
        
        all_issues = result.get_all_issues()
        assert len(all_issues) == 3
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.info) == 1


class TestRuntimeValidator:
    """Test RuntimeValidator class."""
    
    def test_validate_valid_python_file(self, tmp_path):
        """Test validating valid Python file."""
        # Create valid Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    print(hello())
""")
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        assert result.is_valid
        assert not result.has_errors
        assert result.file_path == str(test_file)
    
    def test_validate_invalid_syntax(self, tmp_path):
        """Test validating file with syntax error."""
        # Create file with syntax error
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    return "Hello, World!"
    # Missing closing parenthesis
    print("test"
""")
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        assert not result.is_valid, "File with syntax error should be invalid"
        assert result.has_errors, "Should have errors"
        assert len(result.errors) > 0, "Should have at least one error"
        
        # Check error details
        error = result.errors[0]
        assert error.error_type in ["SyntaxError", "ParseError"]
        assert error.line_number is not None
    
    def test_validate_nonexistent_file(self, tmp_path):
        """Test validating nonexistent file."""
        test_file = tmp_path / "nonexistent.py"
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        assert not result.is_valid
        assert result.has_errors
        assert "FileNotFound" in result.errors[0].error_type
    
    def test_validate_file_with_valid_imports(self, tmp_path):
        """Test file with valid imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import sys
import os
from pathlib import Path

def main():
    print(sys.version)
    print(os.getcwd())
    print(Path.cwd())
""")
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        assert result.is_valid
        # May have info messages about imports, but should be valid
    
    def test_validate_file_with_invalid_imports(self, tmp_path):
        """Test file with invalid imports (warns but doesn't fail)."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import nonexistent_module_12345

def main():
    pass
""")
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        # Syntax is valid, so file is valid
        assert result.is_valid
        # But should have warning/info about import
        assert result.has_warnings or len(result.info) > 0
    
    def test_validate_directory(self, tmp_path):
        """Test validating directory with multiple files."""
        # Create multiple Python files
        (tmp_path / "valid1.py").write_text("def hello(): return 'hello'")
        (tmp_path / "valid2.py").write_text("import sys\ndef main(): print(sys.version)")
        (tmp_path / "invalid.py").write_text("def broken(: pass")  # Syntax error
        
        validator = RuntimeValidator()
        results = validator.validate_directory(tmp_path)
        
        assert len(results) == 3, f"Expected 3 results, got {len(results)}"
        
        # Check individual results
        valid_count = sum(1 for r in results.values() if r.is_valid)
        invalid_count = sum(1 for r in results.values() if not r.is_valid)
        
        assert valid_count == 2, f"Expected 2 valid files, got {valid_count}"
        assert invalid_count == 1, f"Expected 1 invalid file, got {invalid_count}"
    
    def test_validate_directory_with_exclusions(self, tmp_path):
        """Test directory validation with exclusion patterns."""
        # Create files including test files
        (tmp_path / "main.py").write_text("def main(): pass")
        (tmp_path / "test_main.py").write_text("def test_main(): pass")
        
        # Create __pycache__ directory
        pycache = tmp_path / "__pycache__"
        pycache.mkdir()
        (pycache / "main.cpython-39.pyc").write_bytes(b"fake bytecode")
        
        validator = RuntimeValidator()
        results = validator.validate_directory(
            tmp_path,
            exclude_patterns=['**/test_*', '**/__pycache__/*', '**/*.pyc']
        )
        
        # Should only validate main.py
        assert len(results) == 1
        assert any('main.py' in path for path in results.keys())
        assert not any('test_main.py' in path for path in results.keys())
    
    def test_get_summary(self, tmp_path):
        """Test getting validation summary."""
        # Create files
        (tmp_path / "valid.py").write_text("def hello(): return 'hello'")
        (tmp_path / "invalid.py").write_text("def broken(: pass")
        
        validator = RuntimeValidator()
        results = validator.validate_directory(tmp_path)
        
        summary = validator.get_summary()
        
        assert summary['total_files'] == 2
        assert summary['valid_files'] == 1
        assert summary['invalid_files'] == 1
        assert 0 < summary['success_rate'] < 100
        assert summary['total_errors'] > 0


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_validate_file_function(self, tmp_path):
        """Test validate_file convenience function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): return 'hello'")
        
        result = validate_file(str(test_file))
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid
    
    def test_validate_directory_function(self, tmp_path):
        """Test validate_directory convenience function."""
        (tmp_path / "test1.py").write_text("def hello(): return 'hello'")
        (tmp_path / "test2.py").write_text("def world(): return 'world'")
        
        results = validate_directory(str(tmp_path))
        
        assert isinstance(results, dict)
        assert len(results) == 2


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_validate_migrated_code(self, tmp_path):
        """Test validating migrated code with MAF imports."""
        test_file = tmp_path / "migrated_agent.py"
        test_file.write_text("""
# Migrated from Semantic Kernel to MAF
from microsoft.agentframework import Agent, Tool

class MyAgent(Agent):
    def __init__(self, name: str):
        super().__init__(name=name)
    
    @Tool
    def process_data(self, data: str) -> str:
        return f"Processed: {data}"
""")
        
        validator = RuntimeValidator()
        result = validator.validate_file(test_file)
        
        # Syntax should be valid
        assert result.is_valid
        # May have import warnings (MAF not installed in test env)
        # but syntax is correct
    
    def test_validate_multiple_migrated_files(self, tmp_path):
        """Test validating multiple migrated files."""
        # Create multiple migrated files
        files = {
            "agent1.py": """
from microsoft.agentframework import Agent

class Agent1(Agent):
    pass
""",
            "agent2.py": """
from microsoft.agentframework import Agent, Tool

class Agent2(Agent):
    @Tool
    def tool1(self):
        pass
""",
            "utils.py": """
def helper():
    return "helper"
""",
        }
        
        for filename, content in files.items():
            (tmp_path / filename).write_text(content)
        
        validator = RuntimeValidator()
        results = validator.validate_directory(tmp_path)
        
        # All should have valid syntax
        assert len(results) == 3
        
        # Check success rate
        summary = validator.get_summary()
        assert summary['success_rate'] == 100.0

