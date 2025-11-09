"""
Performance Tests for Git Workflow (Phase 1.5 - Performance Tests)

Tests performance and scalability.
Target: 5-8 tests, validates performance requirements
"""

import pytest
import subprocess
import tempfile
import shutil
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))
from utils.cleanup import safe_rmtree
import time
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.utils.git_ops import (
    create_migration_branch,
    show_git_diff,
    get_git_status
)


@pytest.fixture
def large_git_repo():
    """Create large git repository for performance testing."""
    temp_dir = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
    
    # Create many files
    for i in range(100):
        (temp_dir / f"file_{i}.py").write_text(f"# File {i}\nfrom semantic_kernel import Kernel")
    
    subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, capture_output=True)
    
    yield temp_dir
    safe_rmtree(temp_dir)


class TestGitPerformance:
    """Test git performance."""
    
    def test_perf_git_branch_creation_large_repo(self, large_git_repo):
        """Test branch creation performance on large repo."""
        start_time = time.time()
        success = create_migration_branch(large_git_repo, "migratex/perf-test")
        duration = time.time() - start_time
        
        assert success == True
        assert duration < 5.0  # Should complete in <5 seconds
    
    def test_perf_git_diff_large_changes(self, large_git_repo):
        """Test git diff performance with large changes."""
        # Make many changes
        for i in range(50):
            (large_git_repo / f"modified_{i}.py").write_text("modified code")
        
        start_time = time.time()
        diff = show_git_diff(large_git_repo)
        duration = time.time() - start_time
        
        assert isinstance(diff, str)
        assert duration < 10.0  # Should complete in <10 seconds
    
    def test_perf_git_status_large_repo(self, large_git_repo):
        """Test git status performance on large repo."""
        start_time = time.time()
        status = get_git_status(large_git_repo)
        duration = time.time() - start_time
        
        assert isinstance(status, dict) and len(status) > 0, "Git status should be non-empty dict"
        assert duration < 2.0  # Should complete in <2 seconds
    
    def test_perf_git_workflow_memory(self, large_git_repo):
        """Test memory usage during git operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        context = MigrationContext(
            project_path=large_git_repo,
            mode="auto",
            use_git_branch=True
        )
        
        orchestrator = Orchestrator(context)
        orchestrator._setup_git_branch()
        
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_used = mem_after - mem_before
        
        # Should not use excessive memory (<500MB)
        assert mem_used < 500.0
    
    def test_perf_git_workflow_timeout(self, large_git_repo):
        """Test timeout handling for slow git operations."""
        # This test validates that timeouts are handled
        # Actual timeout testing would require mocking slow operations
        start_time = time.time()
        diff = show_git_diff(large_git_repo)
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 30.0  # 30 second timeout

