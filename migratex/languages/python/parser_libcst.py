"""
Python libcst parser for transformations
"""

from pathlib import Path
import libcst as cst


class PythonLibCSTParser:
    """
    High-fidelity AST parser using libcst.
    Used for code transformation phase (preserves formatting/comments).
    """
    
    def parse(self, file_path: Path) -> cst.Module:
        """Parse Python file and return libcst Module."""
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        return cst.parse_module(source_code)
    
    def transform(self, module: cst.Module, transformer: cst.CSTTransformer) -> cst.Module:
        """Apply transformation to module."""
        return module.visit(transformer)

