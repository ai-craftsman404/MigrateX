"""
Unit Tests for Git Operations (Phase 1.5 - Unit Tests)

Tests git utility functions in isolation.
Target: 20-25 tests, 100% coverage of git utilities
"""

import pytest
import subprocess
import tempfile
import shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cleanup import safe_rmtree
from migratex.utils.git_ops import (
    is_git_repo,
    get_git_root,
    get_current_branch,
    branch_exists,
    create_migration_branch,
    show_git_diff,
    get_git_status,
    has_uncommitted_changes,
    stash_changes,
    restore_stash
)


@pytest.fixture
def git_repo():
    """Create a git repository for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_dir, capture_output=True)
    
    # Create initial commit
    (temp_dir / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=temp_dir, capture_output=True)
    
    yield temp_dir
    safe_rmtree(temp_dir)


@pytest.fixture
def non_git_repo():
    """Create a non-git repository for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    (temp_dir / "file.py").write_text("code")
    yield temp_dir
    safe_rmtree(temp_dir)


class TestGitRepoDetection:
    """Test git repository detection."""
    
    def test_is_git_repo_detects_git(self, git_repo):
        """Test detection of git repo at root."""
        assert is_git_repo(git_repo) == True
    
    def test_is_git_repo_detects_nested(self, git_repo):
        """Test detection of git repo in subdirectory."""
        nested = git_repo / "subdir" / "nested"
        nested.mkdir(parents=True)
        assert is_git_repo(nested) == True
    
    def test_is_git_repo_handles_non_git(self, non_git_repo):
        """Test handling of non-git repo."""
        assert is_git_repo(non_git_repo) == False
    
    def test_is_git_repo_handles_missing_git(self, non_git_repo):
        """Test handling of missing .git directory."""
        assert is_git_repo(non_git_repo) == False


class TestGitRoot:
    """Test git root directory detection."""
    
    def test_get_git_root(self, git_repo):
        """Test finding git root from subdirectory."""
        nested = git_repo / "subdir" / "nested"
        nested.mkdir(parents=True)
        root = get_git_root(nested)
        assert root == git_repo.resolve()
    
    def test_get_git_root_at_root(self, git_repo):
        """Test finding git root at root."""
        root = get_git_root(git_repo)
        assert root == git_repo.resolve()
    
    def test_get_git_root_no_repo(self, non_git_repo):
        """Test handling of non-git repo."""
        root = get_git_root(non_git_repo)
        assert root is None


class TestCurrentBranch:
    """Test current branch detection."""
    
    def test_get_current_branch(self, git_repo):
        """Test getting current branch."""
        branch = get_current_branch(git_repo)
        assert branch == "main" or branch == "master"
    
    def test_get_current_branch_detached_head(self, git_repo):
        """Test handling of detached HEAD."""
        # Create a commit and checkout its hash (detached HEAD)
        (git_repo / "file.py").write_text("code")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit"], cwd=git_repo, capture_output=True)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        subprocess.run(["git", "checkout", commit_hash], cwd=git_repo, capture_output=True)
        
        branch = get_current_branch(git_repo)
        # Detached HEAD should return None
        assert branch is None
    
    def test_get_current_branch_no_repo(self, non_git_repo):
        """Test handling of non-git repo."""
        branch = get_current_branch(non_git_repo)
        assert branch is None


class TestBranchOperations:
    """Test branch operations."""
    
    def test_branch_exists(self, git_repo):
        """Test checking if branch exists."""
        assert branch_exists(git_repo, "main") == True or branch_exists(git_repo, "master") == True
        assert branch_exists(git_repo, "nonexistent-branch") == False
    
    def test_branch_exists_remote(self, git_repo):
        """Test checking remote branch existence."""
        # Remote branches require remote setup, so this may return False
        result = branch_exists(git_repo, "main", remote=True)
        assert isinstance(result, bool)
    
    def test_create_migration_branch_new(self, git_repo):
        """Test creating new branch."""
        success = create_migration_branch(git_repo, "migratex/test-branch")
        assert success == True
        
        branch = get_current_branch(git_repo)
        assert branch == "migratex/test-branch"
    
    def test_create_migration_branch_existing(self, git_repo):
        """Test checking out existing branch."""
        # Create branch first
        subprocess.run(["git", "checkout", "-b", "migratex/existing"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "checkout", "main"], cwd=git_repo, capture_output=True)
        
        # Now try to create/checkout
        success = create_migration_branch(git_repo, "migratex/existing")
        assert success == True
        
        branch = get_current_branch(git_repo)
        assert branch == "migratex/existing"
    
    def test_create_migration_branch_detached_head(self, git_repo):
        """Test handling detached HEAD when creating branch."""
        # Create detached HEAD
        (git_repo / "file.py").write_text("code")
        subprocess.run(["git", "add", "."], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit"], cwd=git_repo, capture_output=True)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_repo,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        subprocess.run(["git", "checkout", commit_hash], cwd=git_repo, capture_output=True)
        
        # Should be able to create branch from detached HEAD
        success = create_migration_branch(git_repo, "migratex/from-detached")
        assert success == True
    
    def test_create_migration_branch_uncommitted_changes(self, git_repo):
        """Test handling uncommitted changes when creating branch."""
        # Create uncommitted changes
        (git_repo / "dirty.py").write_text("uncommitted")
        
        # Should still be able to create branch
        success = create_migration_branch(git_repo, "migratex/with-changes")
        assert success == True


class TestGitDiff:
    """Test git diff operations."""
    
    def test_show_git_diff(self, git_repo):
        """Test showing git diff with changes."""
        # Create and commit a file first
        (git_repo / "modified.py").write_text("original content")
        subprocess.run(["git", "add", "modified.py"], cwd=git_repo, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=git_repo, capture_output=True)
        
        # Now make a change
        (git_repo / "modified.py").write_text("from semantic_kernel import Kernel")
        
        diff = show_git_diff(git_repo)
        assert isinstance(diff, str)
        assert len(diff) > 0
    
    def test_show_git_diff_no_changes(self, git_repo):
        """Test showing git diff with no changes."""
        diff = show_git_diff(git_repo)
        assert isinstance(diff, str)
        # May be empty or contain nothing
    
    def test_show_git_diff_staged(self, git_repo):
        """Test showing git diff with staged changes."""
        # Stage a change
        (git_repo / "staged.py").write_text("code")
        subprocess.run(["git", "add", "staged.py"], cwd=git_repo, capture_output=True)
        
        diff = show_git_diff(git_repo, staged=True)
        assert isinstance(diff, str)


class TestGitStatus:
    """Test git status operations."""
    
    def test_get_git_status(self, git_repo):
        """Test getting git status."""
        status = get_git_status(git_repo)
        assert isinstance(status, dict) and len(status) > 0, "Git status should be non-empty dict"
        assert status["is_git_repo"] == True
        assert "branch" in status
        assert "has_changes" in status
    
    def test_get_git_status_clean(self, git_repo):
        """Test getting git status for clean repo."""
        status = get_git_status(git_repo)
        assert status["has_changes"] == False
        assert status["status"] == "clean"
    
    def test_has_uncommitted_changes(self, git_repo):
        """Test detecting uncommitted changes."""
        # Clean repo
        assert has_uncommitted_changes(git_repo) == False
        
        # Add uncommitted change
        (git_repo / "dirty.py").write_text("uncommitted")
        assert has_uncommitted_changes(git_repo) == True
    
    def test_has_uncommitted_changes_clean(self, git_repo):
        """Test detecting clean repo."""
        assert has_uncommitted_changes(git_repo) == False


class TestStashOperations:
    """Test stash operations."""
    
    def test_stash_changes(self, git_repo):
        """Test stashing uncommitted changes."""
        # Create uncommitted changes
        (git_repo / "stash_test.py").write_text("uncommitted")
        # Add file to git index first
        subprocess.run(["git", "add", "stash_test.py"], cwd=git_repo, capture_output=True)
        
        success = stash_changes(git_repo)
        assert success == True
        assert has_uncommitted_changes(git_repo) == False
    
    def test_restore_stash(self, git_repo):
        """Test restoring stashed changes."""
        # Create and stash changes
        (git_repo / "restore_test.py").write_text("to stash")
        stash_changes(git_repo)
        
        # Restore stash
        success = restore_stash(git_repo)
        assert success == True
        assert (git_repo / "restore_test.py").exists()
    
    def test_stash_empty(self, git_repo):
        """Test stashing when no changes."""
        # No changes to stash
        success = stash_changes(git_repo)
        assert success == True  # Should succeed even with no changes

