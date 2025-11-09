"""
Git operations utilities for migration tool.

Provides functions for git repository detection, branch management,
and git diff operations.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any


def is_git_repo(path: Path) -> bool:
    """
    Check if path is a git repository.
    
    Args:
        path: Path to check (can be file or directory)
    
    Returns:
        True if path is within a git repository, False otherwise
    """
    # If path is a file, check its parent directory
    check_path = path if path.is_dir() else path.parent
    
    # Walk up the directory tree to find .git
    current = check_path.resolve()
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists() and (git_dir.is_dir() or git_dir.is_file()):
            return True
        current = current.parent
    
    return False


def get_git_root(path: Path) -> Optional[Path]:
    """
    Find the git root directory for a given path.
    
    Args:
        path: Path to start searching from
    
    Returns:
        Path to git root directory, or None if not in a git repo
    """
    if not is_git_repo(path):
        return None
    
    check_path = path if path.is_dir() else path.parent
    current = check_path.resolve()
    
    while current != current.parent:
        git_dir = current / ".git"
        if git_dir.exists() and (git_dir.is_dir() or git_dir.is_file()):
            return current
        current = current.parent
    
    return None


def get_current_branch(path: Path) -> Optional[str]:
    """
    Get the current git branch name.
    
    Args:
        path: Path within git repository
    
    Returns:
        Branch name, or None if not in git repo or detached HEAD
    """
    git_root = get_git_root(path)
    if not git_root:
        return None
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            branch = result.stdout.strip()
            # Detached HEAD returns "HEAD", not a branch name
            if branch == "HEAD":
                return None
            return branch
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    return None


def branch_exists(path: Path, branch_name: str, remote: bool = False) -> bool:
    """
    Check if a git branch exists.
    
    Args:
        path: Path within git repository
        branch_name: Name of branch to check
        remote: If True, check remote branches
    
    Returns:
        True if branch exists, False otherwise
    """
    git_root = get_git_root(path)
    if not git_root:
        return False
    
    try:
        if remote:
            result = subprocess.run(
                ["git", "branch", "-r", "--list", branch_name],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=5
            )
        
        return result.returncode == 0 and branch_name in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def has_uncommitted_changes(path: Path) -> bool:
    """
    Check if there are uncommitted changes in the git repository.
    
    Args:
        path: Path within git repository
    
    Returns:
        True if there are uncommitted changes, False otherwise
    """
    git_root = get_git_root(path)
    if not git_root:
        return False
    
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def create_migration_branch(path: Path, branch_name: str) -> bool:
    """
    Create and checkout a migration branch.
    If branch already exists, checkout the existing branch.
    
    Args:
        path: Path within git repository
        branch_name: Name of branch to create/checkout
    
    Returns:
        True if successful, False otherwise
    """
    git_root = get_git_root(path)
    if not git_root:
        return False
    
    try:
        # Check if branch exists
        if branch_exists(path, branch_name):
            # Checkout existing branch
            result = subprocess.run(
                ["git", "checkout", branch_name],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        else:
            # Create new branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def show_git_diff(path: Path, staged: bool = False) -> str:
    """
    Show git diff of changes.
    
    Args:
        path: Path within git repository
        staged: If True, show staged changes; if False, show unstaged changes
    
    Returns:
        Git diff output as string
    """
    git_root = get_git_root(path)
    if not git_root:
        return ""
    
    try:
        if staged:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(
                ["git", "diff"],
                cwd=git_root,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    
    return ""


def get_git_status(path: Path) -> Dict[str, Any]:
    """
    Get git status information.
    
    Args:
        path: Path within git repository
    
    Returns:
        Dictionary with git status information
    """
    git_root = get_git_root(path)
    if not git_root:
        return {
            "is_git_repo": False,
            "has_changes": False,
            "branch": None,
            "status": "not_a_git_repo"
        }
    
    try:
        # Get branch name
        branch = get_current_branch(path)
        
        # Get status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        has_changes = result.returncode == 0 and len(result.stdout.strip()) > 0
        
        return {
            "is_git_repo": True,
            "has_changes": has_changes,
            "branch": branch,
            "status": "clean" if not has_changes else "dirty"
        }
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {
            "is_git_repo": True,
            "has_changes": False,
            "branch": None,
            "status": "error"
        }


def stash_changes(path: Path) -> bool:
    """
    Stash uncommitted changes.
    
    Args:
        path: Path within git repository
    
    Returns:
        True if successful, False otherwise
    """
    git_root = get_git_root(path)
    if not git_root:
        return False
    
    # Check if there are changes to stash
    if not has_uncommitted_changes(path):
        return True  # Nothing to stash, consider it success
    
    try:
        result = subprocess.run(
            ["git", "stash", "push", "-m", "MigrateX: Stashed before migration"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def restore_stash(path: Path) -> bool:
    """
    Restore stashed changes.
    
    Args:
        path: Path within git repository
    
    Returns:
        True if successful, False otherwise
    """
    git_root = get_git_root(path)
    if not git_root:
        return False
    
    try:
        # Check if there's a stash
        result = subprocess.run(
            ["git", "stash", "list"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return True  # No stash to restore, consider it success
        
        # Restore stash
        result = subprocess.run(
            ["git", "stash", "pop"],
            cwd=git_root,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

