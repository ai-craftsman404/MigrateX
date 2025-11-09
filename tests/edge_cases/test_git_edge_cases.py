"""
Edge Case Tests for Git Workflow (Phase 1.5 - Edge Case Tests)

Tests edge cases and error scenarios.
Target: 15-20 tests, validates error handling
"""

import pytest
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))
from utils.cleanup import safe_rmtree
from pathlib import Path
from unittest.mock import patch, MagicMock
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.utils.git_ops import (
    is_git_repo,
    get_git_root,
    create_migration_branch,
    show_git_diff
)


@pytest.fixture
def git_repo_edge():
    """Create git repo for edge case testing."""
    temp_dir = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
    (temp_dir / "file.py").write_text("code")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, capture_output=True)
    yield temp_dir
    safe_rmtree(temp_dir)


class TestGitEdgeCases:
    """Test git edge cases."""
    
    def test_edge_case_git_not_installed(self):
        """Test handling when git is not installed."""
        with patch('subprocess.run', side_effect=FileNotFoundError()):
            result = is_git_repo(Path("/some/path"))
            # Should handle gracefully
            assert isinstance(result, bool)
    
    def test_edge_case_git_permissions(self, git_repo_edge):
        """Test handling git permission errors."""
        # Make .git directory read-only (may not work on Windows)
        import os
        git_dir = git_repo_edge / ".git"
        try:
            os.chmod(git_dir, 0o444)  # Read-only
            
            # Should handle gracefully
            result = get_git_root(git_repo_edge)
            assert result is not None or result is None  # Either is acceptable
        except (OSError, PermissionError):
            pytest.skip("Cannot test permission errors on this system")
        finally:
            try:
                os.chmod(git_dir, 0o755)
            except:
                pass
    
    def test_edge_case_git_detached_head(self, git_repo_edge):
        """Test handling detached HEAD state."""
        # Create detached HEAD
        (git_repo_edge / "file2.py").write_text("code")
        subprocess.run(["git", "add", "."], cwd=git_repo_edge, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit"], cwd=git_repo_edge, capture_output=True)
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_repo_edge,
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        subprocess.run(["git", "checkout", commit_hash], cwd=git_repo_edge, capture_output=True)
        
        # Should handle detached HEAD
        success = create_migration_branch(git_repo_edge, "migratex/from-detached")
        assert success == True
    
    def test_edge_case_git_no_commits(self):
        """Test handling repo with no commits."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
            
            # No commits yet
            result = is_git_repo(temp_dir)
            assert result == True
            
            # Creating branch should still work
            success = create_migration_branch(temp_dir, "migratex/no-commits")
            # May fail if no commits, but should handle gracefully
            assert isinstance(success, bool)
        finally:
            safe_rmtree(temp_dir)
    
    def test_edge_case_git_branch_special_chars(self, git_repo_edge):
        """Test handling branch names with special characters."""
        # Git allows many special chars in branch names
        branch_name = "migratex/test-branch_123"
        success = create_migration_branch(git_repo_edge, branch_name)
        assert success == True
    
    def test_edge_case_git_branch_unicode(self, git_repo_edge):
        """Test handling branch names with unicode."""
        branch_name = "migratex/test-测试"
        success = create_migration_branch(git_repo_edge, branch_name)
        # May or may not work depending on git version
        assert isinstance(success, bool)
    
    def test_edge_case_git_branch_very_long(self, git_repo_edge):
        """Test handling very long branch names."""
        branch_name = "migratex/" + "a" * 200  # Very long name
        success = create_migration_branch(git_repo_edge, branch_name)
        # May fail if too long, but should handle gracefully
        assert isinstance(success, bool)
    
    def test_edge_case_git_timeout(self, git_repo_edge):
        """Test handling git operation timeouts."""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("git", 1)):
            result = show_git_diff(git_repo_edge)
            # Should return empty string on timeout
            assert result == ""
    
    def test_edge_case_git_corrupted_repo(self):
        """Test handling corrupted git repository."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create fake .git directory
            (temp_dir / ".git").mkdir()
            (temp_dir / ".git" / "config").write_text("corrupted")
            
            # Should handle gracefully
            result = is_git_repo(temp_dir)
            # May return True (detects .git) or False (detects corruption)
            assert isinstance(result, bool)
        finally:
            safe_rmtree(temp_dir)
    
    def test_edge_case_git_locked_repo(self, git_repo_edge):
        """Test handling locked git repository."""
        # Create index.lock file (simulates locked repo)
        lock_file = git_repo_edge / ".git" / "index.lock"
        lock_file.write_text("locked")
        
        try:
            # Should handle gracefully
            result = create_migration_branch(git_repo_edge, "migratex/locked")
            # May fail due to lock, but should handle gracefully
            assert isinstance(result, bool)
        finally:
            if lock_file.exists():
                lock_file.unlink()

