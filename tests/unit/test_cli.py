"""
Unit tests for CLI & Orchestration (Agent 1 - T1.4)

Tests command parsing, option validation, error propagation, and user interaction.
Target: 25+ test cases, 85%+ coverage
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from click.testing import CliRunner
from migratex.cli.apply import apply_command
from migratex.core.context import MigrationContext
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestCLI:
    """Test CLI command parsing and validation."""
    
    def test_apply_command_requires_auto_or_review(self):
        """Test that apply command requires --auto or --review."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture)]
            )
            
            assert result.exit_code != 0
            assert "Must specify either --auto or --review" in result.output
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_rejects_both_auto_and_review(self):
        """Test that apply command rejects both --auto and --review."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--review"]
            )
            
            assert result.exit_code != 0
            assert "Cannot use both --auto and --review" in result.output
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_auto_mode(self):
        """Test apply command with --auto mode."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto"],
                catch_exceptions=False
            )
            
            # Should execute (may fail if no patterns, but should not error on CLI)
            assert result.exit_code in [0, 1], f"CLI should execute cleanly, got exit code {result.exit_code}"
            # Verify command actually ran (not just crashed)
            assert result.output is not None and len(result.output) > 0, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_output_dir(self):
        """Test apply command with --output-dir option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        output_dir = Path(tempfile.mkdtemp())
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--output-dir", str(output_dir)],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
            if "Output directory" in result.output:
                assert str(output_dir) in result.output
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
            if output_dir.exists():
                shutil.rmtree(output_dir)
    
    def test_apply_command_with_report_file(self):
        """Test apply command with --report option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        report_file = Path(tempfile.mkdtemp()) / "report.json"
        
        # Create dummy report
        import json
        report_file.write_text(json.dumps({"patterns": []}))
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--report", str(report_file)],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
            if report_file.parent.exists():
                shutil.rmtree(report_file.parent)
    
    def test_apply_command_with_pattern_cache(self):
        """Test apply command with --pattern-cache option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        cache_file = Path(tempfile.mkdtemp()) / "cache.yaml"
        cache_file.write_text("patterns: []")
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--pattern-cache", str(cache_file)],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
            if cache_file.parent.exists():
                shutil.rmtree(cache_file.parent)
    
    def test_apply_command_with_remember_decisions(self):
        """Test apply command with --remember-decisions flag."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--remember-decisions"],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_diff_flag(self):
        """Test apply command with --diff flag."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--diff"],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_review_mode(self):
        """Test apply command with --review-mode option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            for mode in ["pattern", "file", "none"]:
                result = runner.invoke(
                    apply_command,
                    [str(fixture), "--auto", "--review-mode", mode],
                    catch_exceptions=False
                )
                
                # Should execute
                assert result.exit_code in [0, 1]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_on_error_option(self):
        """Test apply command with --on-error option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            for policy in ["continue", "stop"]:
                result = runner.invoke(
                    apply_command,
                    [str(fixture), "--auto", "--on-error", policy],
                    catch_exceptions=False
                )
                
                # Should execute
                assert result.exit_code in [0, 1]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_apply_command_with_summary_output(self):
        """Test apply command with --summary option."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        summary_file = Path(tempfile.mkdtemp()) / "summary.md"
        
        try:
            result = runner.invoke(
                apply_command,
                [str(fixture), "--auto", "--summary", str(summary_file)],
                catch_exceptions=False
            )
            
            # Should execute cleanly
            assert result.exit_code in [0, 1], f"CLI should execute, got exit code {result.exit_code}"
            assert result.output is not None, "CLI should produce output"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
            if summary_file.parent.exists():
                shutil.rmtree(summary_file.parent)
    
    def test_apply_command_nonexistent_path(self):
        """Test apply command with nonexistent path."""
        runner = CliRunner()
        nonexistent = Path("/nonexistent/path/to/project")
        
        result = runner.invoke(
            apply_command,
            [str(nonexistent), "--auto"]
        )
        
        assert result.exit_code != 0
    
    def test_apply_command_file_path_not_directory(self):
        """Test apply command rejects file path (requires directory)."""
        runner = CliRunner()
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        file_path = fixture / "main.py"
        
        try:
            result = runner.invoke(
                apply_command,
                [str(file_path), "--auto"]
            )
            
            # Should reject file path
            assert result.exit_code != 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)


class TestOrchestration:
    """Test orchestration logic."""
    
    def test_context_creation_with_output_dir(self):
        """Test MigrationContext creation with output_dir."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        output_dir = Path(tempfile.mkdtemp())
        
        try:
            context = MigrationContext(
                project_path=fixture,
                mode="auto",
                output_dir=output_dir
            )
            
            assert context.output_dir == output_dir
            assert context.project_path == fixture
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
            if output_dir.exists():
                shutil.rmtree(output_dir)
    
    def test_context_error_policy(self):
        """Test MigrationContext error policy setting."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            for policy in ["continue", "stop"]:
                context = MigrationContext(
                    project_path=fixture,
                    mode="auto",
                    error_policy=policy
                )
                
                assert context.error_policy == policy
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_context_review_granularity(self):
        """Test MigrationContext review granularity setting."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            for granularity in ["pattern", "file", "none"]:
                context = MigrationContext(
                    project_path=fixture,
                    mode="review",
                    review_granularity=granularity
                )
                
                assert context.review_granularity == granularity
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_context_remember_decisions(self):
        """Test MigrationContext remember_decisions setting."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            context = MigrationContext(
                project_path=fixture,
                mode="review",
                remember_decisions=True
            )
            
            assert context.remember_decisions == True
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_context_outlier_mode(self):
        """Test MigrationContext outlier_mode setting."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            for mode in ["cautious", "review", "expert", None]:
                context = MigrationContext(
                    project_path=fixture,
                    mode="auto",
                    outlier_mode=mode
                )
                
                assert context.outlier_mode == mode
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_context_interactive_flag(self):
        """Test MigrationContext interactive flag."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        
        try:
            context = MigrationContext(
                project_path=fixture,
                mode="auto",
                interactive=False
            )
            
            assert context.interactive == False
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

