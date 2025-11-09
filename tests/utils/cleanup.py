"""
Windows-safe cleanup utilities for test fixtures.
"""

import shutil
import time
from pathlib import Path
from typing import Optional


def safe_rmtree(path: Path, max_retries: int = 3, delay: float = 0.1):
    """
    Safely remove directory tree with retry logic for Windows file locks.
    
    On Windows, git files may be locked briefly after operations.
    This function retries with delays to handle this.
    """
    if not path.exists():
        return
    
    for attempt in range(max_retries):
        try:
            shutil.rmtree(path, ignore_errors=True)
            # Verify deletion
            if not path.exists():
                return
        except (PermissionError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
            else:
                # Last attempt - try with ignore_errors=True
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    pass  # Give up, let OS clean up later


def ensure_parent_dir(file_path: Path):
    """Ensure parent directory exists before writing file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

