"""
Python AST parser for analysis (using built-in ast module)
"""

import ast
from pathlib import Path
from typing import Dict, Any


class PythonASTParser:
    """
    Fast AST parser using Python's built-in ast module.
    Used for analysis and discovery phase.
    """
    
    def parse(self, file_path: Path) -> ast.AST:
        """Parse Python file and return AST."""
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        
        return ast.parse(source_code, filename=str(file_path))
    
    def get_imports(self, tree: ast.AST) -> list[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

