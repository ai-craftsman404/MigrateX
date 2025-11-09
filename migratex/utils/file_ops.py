"""
File operations utilities for migration tool
"""

import shutil
from pathlib import Path
from typing import Set


def copy_project_structure(source: Path, destination: Path, exclude_patterns: Set[str] = None) -> None:
    """
    Copy entire project structure to destination directory.
    
    Args:
        source: Source project directory
        destination: Destination directory (will be created if needed)
        exclude_patterns: Set of patterns to exclude (e.g., {'.git', '__pycache__', '*.pyc'})
    
    This preserves directory structure and copies all files.
    """
    if exclude_patterns is None:
        exclude_patterns = {
            '.git', '__pycache__', '.pytest_cache', '.mypy_cache',
            '*.pyc', '*.pyo', '.DS_Store', 'node_modules', 'venv', 'env'
        }
    
    destination.mkdir(parents=True, exist_ok=True)
    
    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded."""
        # Check directory names
        if any(part in exclude_patterns for part in path.parts):
            return True
        
        # Check file extensions
        if path.is_file():
            for pattern in exclude_patterns:
                if pattern.startswith('*') and path.suffix == pattern[1:]:
                    return True
        
        return False
    
    # Copy all files and directories
    for item in source.rglob('*'):
        if should_exclude(item):
            continue
        
        relative_path = item.relative_to(source)
        dest_path = destination / relative_path
        
        if item.is_dir():
            dest_path.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest_path)

