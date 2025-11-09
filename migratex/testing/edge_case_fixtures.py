"""
Comprehensive edge case test fixtures and utilities
"""

from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil


class EdgeCaseTestFixtures:
    """
    Provides test fixtures for edge cases and outliers.
    Creates temporary codebases with specific edge case scenarios.
    """
    
    @staticmethod
    def create_empty_codebase() -> Path:
        """Create empty codebase (no Python files)."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "README.md").write_text("# Empty Project")
        return temp_dir
    
    @staticmethod
    def create_single_file_codebase(content: str) -> Path:
        """Create codebase with single Python file."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "main.py").write_text(content, encoding="utf-8")
        return temp_dir
    
    @staticmethod
    def create_syntax_error_codebase() -> Path:
        """Create codebase with syntax errors."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "broken.py").write_text("def broken(\n    return  # Missing closing paren")
        return temp_dir
    
    @staticmethod
    def create_mixed_frameworks_codebase() -> Path:
        """Create codebase with both SK and AutoGen."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "sk_file.py").write_text("from semantic_kernel import Kernel")
        (temp_dir / "autogen_file.py").write_text("from autogen import ConversableAgent")
        return temp_dir
    
    @staticmethod
    def create_aliased_imports_codebase() -> Path:
        """Create codebase with aliased imports."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "aliased.py").write_text("import semantic_kernel as sk\nfrom autogen import ConversableAgent as CAgent")
        return temp_dir
    
    @staticmethod
    def create_pattern_in_comments_codebase() -> Path:
        """Create codebase with patterns only in comments."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "commented.py").write_text("# from semantic_kernel import Kernel\n# This is commented out")
        return temp_dir
    
    @staticmethod
    def create_circular_dependency_codebase() -> Path:
        """Create codebase with circular import dependencies."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "a.py").write_text("from b import B\nfrom semantic_kernel import Kernel")
        (temp_dir / "b.py").write_text("from a import A")
        return temp_dir
    
    @staticmethod
    def create_large_file_codebase(lines: int = 10000) -> Path:
        """Create codebase with very large file."""
        temp_dir = Path(tempfile.mkdtemp())
        content = "from semantic_kernel import Kernel\n\n" + "\n".join([f"# Line {i}" for i in range(lines)])
        (temp_dir / "large.py").write_text(content)
        return temp_dir
    
    @staticmethod
    def create_deep_nested_codebase(levels: int = 20) -> Path:
        """Create codebase with deeply nested directory structure."""
        temp_dir = Path(tempfile.mkdtemp())
        current = temp_dir
        for i in range(levels):
            current = current / f"level_{i}"
            current.mkdir()
        (current / "deep.py").write_text("from semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_encoding_issue_codebase() -> Path:
        """Create codebase with encoding issues."""
        temp_dir = Path(tempfile.mkdtemp())
        # Write file with non-UTF-8 encoding (simulate)
        (temp_dir / "encoded.py").write_bytes(b"# -*- coding: latin-1 -*-\nfrom semantic_kernel import Kernel\n\xe9")  # é in latin-1
        return temp_dir
    
    @staticmethod
    def create_pattern_conflict_codebase() -> Path:
        """Create codebase where multiple patterns match same code."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "conflict.py").write_text("from semantic_kernel import Kernel, Plugin\nfrom autogen import ConversableAgent")
        return temp_dir
    
    @staticmethod
    def cleanup(temp_dir: Path):
        """Clean up temporary directory."""
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


class OutlierTestFixtures:
    """
    Provides test fixtures for outlier scenarios.
    """
    
    @staticmethod
    def create_monorepo_structure() -> Path:
        """Create monorepo with multiple projects."""
        temp_dir = Path(tempfile.mkdtemp())
        # Ensure parent directories exist
        (temp_dir / "project1").mkdir(parents=True, exist_ok=True)
        (temp_dir / "project2").mkdir(parents=True, exist_ok=True)
        (temp_dir / "project1" / "main.py").write_text("from semantic_kernel import Kernel")
        (temp_dir / "project2" / "main.py").write_text("from autogen import ConversableAgent")
        return temp_dir
    
    @staticmethod
    def create_namespace_package_codebase() -> Path:
        """Create codebase with namespace packages."""
        temp_dir = Path(tempfile.mkdtemp())
        # Ensure parent directories exist
        (temp_dir / "namespace" / "package").mkdir(parents=True, exist_ok=True)
        (temp_dir / "namespace" / "package" / "__init__.py").write_text("")
        (temp_dir / "namespace" / "package" / "module.py").write_text("from semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_generated_code_codebase() -> Path:
        """Create codebase with generated code directories."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "generated").mkdir(parents=True, exist_ok=True)
        (temp_dir / "generated" / "code.py").write_text("# Generated code\nfrom semantic_kernel import Kernel")
        (temp_dir / ".gitignore").write_text("generated/")
        return temp_dir
    
    @staticmethod
    def create_build_artifacts_codebase() -> Path:
        """Create codebase with build artifacts."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "__pycache__").mkdir(parents=True, exist_ok=True)
        (temp_dir / "__pycache__" / "module.cpython-39.pyc").write_bytes(b"dummy bytecode")
        (temp_dir / "main.py").write_text("from semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_venv_codebase() -> Path:
        """Create codebase with virtual environment."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "venv" / "lib" / "python3.9" / "site-packages").mkdir(parents=True, exist_ok=True)
        (temp_dir / "venv" / "lib" / "python3.9" / "site-packages" / "sk.py").write_text("from semantic_kernel import Kernel")
        (temp_dir / "main.py").write_text("from semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_multiple_python_versions_codebase() -> Path:
        """Create codebase with multiple Python version directories."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "python2").mkdir(parents=True, exist_ok=True)
        (temp_dir / "python3").mkdir(parents=True, exist_ok=True)
        (temp_dir / "python2" / "code.py").write_text("# Python 2 code\nfrom semantic_kernel import Kernel")
        (temp_dir / "python3" / "code.py").write_text("# Python 3 code\nfrom semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_custom_python_paths_codebase() -> Path:
        """Create codebase with custom Python paths."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "custom" / "python" / "lib").mkdir(parents=True, exist_ok=True)
        (temp_dir / "custom" / "python" / "lib" / "code.py").write_text("from semantic_kernel import Kernel")
        return temp_dir
    
    @staticmethod
    def create_mixed_project_types_codebase() -> Path:
        """Create codebase with mixed project types."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "backend").mkdir(parents=True, exist_ok=True)
        (temp_dir / "frontend").mkdir(parents=True, exist_ok=True)
        (temp_dir / "backend" / "app.py").write_text("from semantic_kernel import Kernel")
        (temp_dir / "frontend" / "app.js").write_text("// Frontend code")
        return temp_dir
    
    @staticmethod
    def cleanup(temp_dir: Path):
        """Clean up temporary directory."""
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

