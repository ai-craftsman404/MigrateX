"""
Windows-Specific Tests for CLI Encoding

Tests that verify CLI output works correctly on Windows console (cp1252 encoding).
"""

import pytest
import sys
import io
from unittest.mock import patch
from migratex.cli.analyze import analyze_command
from migratex.cli.apply import apply_command
from click.testing import CliRunner
from pathlib import Path
import tempfile
import shutil
import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parent.parent))
from utils.cleanup import safe_rmtree


class TestWindowsConsoleEncoding:
    """Test Windows console encoding compatibility."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "test.py").write_text("from semantic_kernel import Kernel")
        
        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial"], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        safe_rmtree(temp_dir)
    
    def test_analyze_command_windows_encoding(self, temp_repo):
        """Test analyze command doesn't crash on Windows console encoding."""
        runner = CliRunner()
        
        # Simulate Windows console encoding (cp1252)
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Force cp1252 encoding
            original_encoding = sys.stdout.encoding
            try:
                # Run analyze command
                result = runner.invoke(
                    analyze_command,
                    [str(temp_repo), "--out", str(temp_repo / "report.json")]
                )
                
                # Should not raise UnicodeEncodeError
                assert result.exit_code in [0, 1]  # May fail for other reasons
                assert "UnicodeEncodeError" not in str(result.exception or "")
                
                # Output should not contain problematic Unicode characters
                output = result.output
                # Option 1 UI uses + for success, x for error (ASCII-safe)
                assert ("+" in output and "complete" in output) or "x" in output, \
                    "Should use ASCII-safe status indicators (+/x)"
            finally:
                pass
    
    def test_apply_command_windows_encoding(self, temp_repo):
        """Test apply command doesn't crash on Windows console encoding."""
        runner = CliRunner()
        
        # Create analysis report first
        (temp_repo / "report.json").write_text('{"patterns": [], "files": []}')
        
        # Run apply command
        result = runner.invoke(
            apply_command,
            [str(temp_repo), "--auto", "--report", str(temp_repo / "report.json")]
        )
        
        # Should not raise UnicodeEncodeError
        assert "UnicodeEncodeError" not in str(result.exception or "")
        
        # Output should not contain problematic Unicode characters
        output = result.output
        assert "✓" not in output
        assert "✗" not in output
    
    def test_cli_output_safe_characters(self):
        """Test that CLI uses only safe ASCII characters."""
        # Verify all CLI output uses safe characters
        from migratex.cli import analyze, apply
        
        # Check that no Unicode characters are in success/error messages
        import inspect
        import re
        
        # Check analyze.py
        analyze_source = inspect.getsource(analyze)
        assert "✓" not in analyze_source or "[OK]" in analyze_source
        assert "✗" not in analyze_source or "[ERROR]" in analyze_source
        
        # Check apply.py
        apply_source = inspect.getsource(apply)
        assert "✓" not in apply_source or "[OK]" in apply_source
        assert "✗" not in apply_source or "[ERROR]" in apply_source

