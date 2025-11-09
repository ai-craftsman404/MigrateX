"""
Integration Tests for Git Branch Workflow (Phase 1.5 - Branch Workflow Tests)

Tests branch lifecycle and state management.
Target: 10-12 tests, validates branch workflow
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
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.utils.git_ops import (
    get_current_branch,
    create_migration_branch,
    branch_exists
)


@pytest.fixture
def git_repo_branch():
    """Create git repo for branch workflow testing."""
    temp_dir = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
    (temp_dir / "main.py").write_text("from semantic_kernel import Kernel")
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, capture_output=True)
    yield temp_dir
    safe_rmtree(temp_dir)


class TestGitBranchWorkflow:
    """Test git branch workflow."""
    
    def test_branch_creation_before_migration(self, git_repo_branch):
        """Test branch creation before migration."""
        context = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name="migratex/pre-migration"
        )
        
        orchestrator = Orchestrator(context)
        orchestrator._setup_git_branch()
        
        branch = get_current_branch(git_repo_branch)
        assert branch == "migratex/pre-migration"
    
    def test_checkout_existing_branch(self, git_repo_branch):
        """Test checking out existing branch."""
        # Create branch first
        subprocess.run(
            ["git", "checkout", "-b", "migratex/existing"],
            cwd=git_repo_branch,
            capture_output=True
        )
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=git_repo_branch,
            capture_output=True
        )
        
        context = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name="migratex/existing"
        )
        
        orchestrator = Orchestrator(context)
        orchestrator._setup_git_branch()
        
        branch = get_current_branch(git_repo_branch)
        assert branch == "migratex/existing"
    
    def test_original_branch_preserved(self, git_repo_branch):
        """Test that original branch is preserved."""
        original = get_current_branch(git_repo_branch)
        
        context = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name="migratex/test"
        )
        
        orchestrator = Orchestrator(context)
        orchestrator._setup_git_branch()
        
        assert context.original_branch == original
    
    def test_multiple_migrations_same_branch(self, git_repo_branch):
        """Test multiple migrations on same branch."""
        branch_name = "migratex/multi-migration"
        
        # First migration
        context1 = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name=branch_name
        )
        orchestrator1 = Orchestrator(context1)
        orchestrator1._setup_git_branch()
        
        # Second migration
        context2 = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name=branch_name
        )
        orchestrator2 = Orchestrator(context2)
        orchestrator2._setup_git_branch()
        
        branch = get_current_branch(git_repo_branch)
        assert branch == branch_name
    
    def test_branch_switching(self, git_repo_branch):
        """Test switching between branches."""
        # Create multiple branches
        subprocess.run(
            ["git", "checkout", "-b", "migratex/branch1"],
            cwd=git_repo_branch,
            capture_output=True
        )
        subprocess.run(
            ["git", "checkout", "-b", "migratex/branch2"],
            cwd=git_repo_branch,
            capture_output=True
        )
        
        # Switch back to branch1
        context = MigrationContext(
            project_path=git_repo_branch,
            mode="auto",
            use_git_branch=True,
            git_branch_name="migratex/branch1"
        )
        
        orchestrator = Orchestrator(context)
        orchestrator._setup_git_branch()
        
        branch = get_current_branch(git_repo_branch)
        assert branch == "migratex/branch1"
    
    def test_branch_exists_check(self, git_repo_branch):
        """Test branch existence checking."""
        # Create branch
        create_migration_branch(git_repo_branch, "migratex/exists-test")
        
        # Check existence
        assert branch_exists(git_repo_branch, "migratex/exists-test") == True
        assert branch_exists(git_repo_branch, "migratex/nonexistent") == False

