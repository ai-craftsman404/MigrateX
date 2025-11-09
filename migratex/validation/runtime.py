"""
Runtime Validation Module

Validates migrated code at runtime to ensure:
- Syntax correctness (Python AST parsing)
- Import validity (can imports be resolved)
- File-level correctness (proper structure, no critical errors)
- Directory-level consistency (all files validate)

Architecture:
- Uses Python ast module for syntax validation
- Checks import statements for validity
- Provides clear error messages with line numbers
- Integrates into migration workflow

Usage:
    from migratex.validation import RuntimeValidator, validate_file
    
    # Validate single file
    result = validate_file("path/to/file.py")
    if result.is_valid:
        print("✅ File is valid")
    else:
        print(f"❌ Errors: {result.errors}")
    
    # Validate directory
    validator = RuntimeValidator()
    results = validator.validate_directory("path/to/dir")
"""

import ast
import sys
import importlib.util
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Represents a validation error."""
    level: ValidationLevel
    file_path: str
    line_number: Optional[int]
    column_number: Optional[int]
    error_type: str
    message: str
    context: Optional[str] = None
    
    def __str__(self) -> str:
        """Format error for display."""
        location = f"{self.file_path}"
        if self.line_number:
            location += f":{self.line_number}"
            if self.column_number:
                location += f":{self.column_number}"
        
        return f"[{self.level.value.upper()}] {location} - {self.error_type}: {self.message}"


@dataclass
class ValidationResult:
    """Result of validation."""
    file_path: str
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    def add_error(self, error: ValidationError) -> None:
        """Add error to result."""
        if error.level == ValidationLevel.ERROR:
            self.errors.append(error)
            self.is_valid = False
        elif error.level == ValidationLevel.WARNING:
            self.warnings.append(error)
        else:
            self.info.append(error)
    
    def get_all_issues(self) -> List[ValidationError]:
        """Get all issues (errors + warnings + info)."""
        return self.errors + self.warnings + self.info


class RuntimeValidator:
    """
    Runtime validator for migrated code.
    
    Validates:
    1. Syntax correctness (using ast.parse)
    2. Import validity (can imports be resolved)
    3. File-level correctness (proper structure)
    4. Directory-level consistency (all files valid)
    """
    
    def __init__(self):
        """Initialize validator."""
        self.validated_files: Set[Path] = set()
        self.results: Dict[str, ValidationResult] = {}
    
    def validate_file(self, file_path: Path) -> ValidationResult:
        """
        Validate a single Python file.
        
        Args:
            file_path: Path to Python file to validate
            
        Returns:
            ValidationResult with errors/warnings
        """
        file_path = Path(file_path)
        
        # Create result object
        result = ValidationResult(
            file_path=str(file_path),
            is_valid=True
        )
        
        # Check file exists
        if not file_path.exists():
            result.add_error(ValidationError(
                level=ValidationLevel.ERROR,
                file_path=str(file_path),
                line_number=None,
                column_number=None,
                error_type="FileNotFound",
                message=f"File does not exist: {file_path}"
            ))
            return result
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            result.add_error(ValidationError(
                level=ValidationLevel.ERROR,
                file_path=str(file_path),
                line_number=None,
                column_number=None,
                error_type="ReadError",
                message=f"Error reading file: {str(e)}"
            ))
            return result
        
        # Validate syntax
        self._validate_syntax(file_path, content, result)
        
        # Validate imports (only if syntax is valid)
        if result.is_valid:
            self._validate_imports(file_path, content, result)
        
        # Store result
        self.results[str(file_path)] = result
        self.validated_files.add(file_path)
        
        return result
    
    def _validate_syntax(
        self, 
        file_path: Path, 
        content: str, 
        result: ValidationResult
    ) -> None:
        """Validate Python syntax using ast.parse."""
        try:
            ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            result.add_error(ValidationError(
                level=ValidationLevel.ERROR,
                file_path=str(file_path),
                line_number=e.lineno,
                column_number=e.offset,
                error_type="SyntaxError",
                message=e.msg,
                context=e.text.strip() if e.text else None
            ))
        except Exception as e:
            result.add_error(ValidationError(
                level=ValidationLevel.ERROR,
                file_path=str(file_path),
                line_number=None,
                column_number=None,
                error_type="ParseError",
                message=f"Error parsing file: {str(e)}"
            ))
    
    def _validate_imports(
        self, 
        file_path: Path, 
        content: str, 
        result: ValidationResult
    ) -> None:
        """Validate import statements."""
        try:
            tree = ast.parse(content, filename=str(file_path))
        except:
            # Already reported in _validate_syntax
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._check_import(alias.name, file_path, node.lineno, result)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._check_import(node.module, file_path, node.lineno, result)
    
    def _check_import(
        self, 
        module_name: str, 
        file_path: Path, 
        line_number: int, 
        result: ValidationResult
    ) -> None:
        """Check if import can be resolved."""
        # Skip relative imports (hard to validate without execution)
        if module_name.startswith('.'):
            return
        
        # Skip common built-in modules
        if module_name.split('.')[0] in sys.builtin_module_names:
            return
        
        # Try to find module spec
        try:
            spec = importlib.util.find_spec(module_name.split('.')[0])
            if spec is None:
                result.add_error(ValidationError(
                    level=ValidationLevel.WARNING,
                    file_path=str(file_path),
                    line_number=line_number,
                    column_number=None,
                    error_type="ImportWarning",
                    message=f"Cannot resolve import: {module_name}"
                ))
        except (ImportError, ModuleNotFoundError, ValueError):
            # Some imports may be valid but not resolvable at validation time
            result.add_error(ValidationError(
                level=ValidationLevel.INFO,
                file_path=str(file_path),
                line_number=line_number,
                column_number=None,
                error_type="ImportInfo",
                message=f"Import may not be installed: {module_name}"
            ))
        except Exception:
            # Ignore other exceptions (e.g., circular imports during validation)
            pass
    
    def validate_directory(
        self, 
        directory: Path, 
        pattern: str = "**/*.py",
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, ValidationResult]:
        """
        Validate all Python files in a directory.
        
        Args:
            directory: Directory to validate
            pattern: Glob pattern for files (default: **/*.py)
            exclude_patterns: Patterns to exclude (e.g., ['**/test_*', '**/__pycache__/*'])
            
        Returns:
            Dict mapping file paths to ValidationResults
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        # Default exclusions
        if exclude_patterns is None:
            exclude_patterns = ['**/__pycache__/*', '**/*.pyc', '**/.git/*']
        
        # Find all Python files
        python_files = list(directory.glob(pattern))
        
        # Filter by exclusion patterns
        filtered_files = []
        for file_path in python_files:
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_files.append(file_path)
        
        # Validate each file
        results = {}
        for file_path in filtered_files:
            result = self.validate_file(file_path)
            results[str(file_path)] = result
        
        return results
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get validation summary statistics.
        
        Returns:
            Dict with summary statistics
        """
        total_files = len(self.results)
        valid_files = sum(1 for r in self.results.values() if r.is_valid)
        invalid_files = total_files - valid_files
        
        total_errors = sum(len(r.errors) for r in self.results.values())
        total_warnings = sum(len(r.warnings) for r in self.results.values())
        total_info = sum(len(r.info) for r in self.results.values())
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'success_rate': (valid_files / total_files * 100) if total_files > 0 else 0,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'total_info': total_info,
        }
    
    def print_summary(self) -> None:
        """Print validation summary to console."""
        summary = self.get_summary()
        
        print("\n" + "=" * 80)
        print("RUNTIME VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Files:    {summary['total_files']}")
        print(f"Valid Files:    {summary['valid_files']} ✅")
        print(f"Invalid Files:  {summary['invalid_files']} ❌")
        print(f"Success Rate:   {summary['success_rate']:.1f}%")
        print(f"\nErrors:   {summary['total_errors']}")
        print(f"Warnings: {summary['total_warnings']}")
        print(f"Info:     {summary['total_info']}")
        print("=" * 80 + "\n")


# Convenience functions

def validate_file(file_path: str) -> ValidationResult:
    """
    Validate a single file (convenience function).
    
    Args:
        file_path: Path to file to validate
        
    Returns:
        ValidationResult
    """
    validator = RuntimeValidator()
    return validator.validate_file(Path(file_path))


def validate_directory(
    directory: str, 
    pattern: str = "**/*.py",
    exclude_patterns: Optional[List[str]] = None
) -> Dict[str, ValidationResult]:
    """
    Validate all files in directory (convenience function).
    
    Args:
        directory: Directory to validate
        pattern: Glob pattern for files
        exclude_patterns: Patterns to exclude
        
    Returns:
        Dict mapping file paths to ValidationResults
    """
    validator = RuntimeValidator()
    return validator.validate_directory(Path(directory), pattern, exclude_patterns)

