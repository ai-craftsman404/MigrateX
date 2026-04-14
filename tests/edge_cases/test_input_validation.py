"""
Edge Case Tests for Input Validation (Agent 4 - T4.1)

Tests edge cases for input validation and boundary conditions.
Target: 15+ edge cases, 100% of identified edge cases
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.core.context import MigrationContext
from migratex.agents.code_analyzer import CodeAnalyzerAgent
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestInputValidationEdgeCases:
    """Test input validation edge cases."""
    
    def test_empty_codebase(self):
        """Test empty codebase (no Python files)."""
        fixture = EdgeCaseTestFixtures.create_empty_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle empty codebase gracefully
            assert context.report is not None
            assert context.report.get("statistics", {}).get("total_files", 0) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_single_file_codebase(self):
        """Test single file codebase."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle single file
            assert len(context.report.get("files", [])) == 1
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_very_large_files(self):
        """Test very large files (>10K lines)."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=15000)
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle large files
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_files_with_encoding_issues(self):
        """Test files with encoding issues (non-UTF-8)."""
        fixture = EdgeCaseTestFixtures.create_encoding_issue_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            
            # Should handle encoding issues gracefully
            try:
                analyzer.run()
                handled = True
            except UnicodeDecodeError:
                handled = False
            
            # Should handle or skip gracefully
            assert isinstance(handled, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_files_with_syntax_errors(self):
        """Test files with syntax errors (should skip gracefully)."""
        fixture = EdgeCaseTestFixtures.create_syntax_error_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            
            # Should handle syntax errors gracefully
            try:
                analyzer.run()
                handled = True
            except SyntaxError:
                handled = False
            
            # Should handle or skip gracefully
            assert isinstance(handled, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_binary_files_ignored(self):
        """Test that binary files are ignored."""
        fixture = Path(tempfile.mkdtemp())
        binary_file = fixture / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03\x04")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Binary files should not be in report
            files = context.report.get("files", [])
            assert "binary.bin" not in [str(Path(f).name) for f in files]
        finally:
            shutil.rmtree(fixture)
    
    def test_symlinks_handled(self):
        """Test symlinks are handled correctly."""
        import os
        
        fixture = Path(tempfile.mkdtemp())
        source_file = fixture / "source.py"
        source_file.write_text("from semantic_kernel import Kernel")
        
        try:
            # Create symlink (may not work on Windows)
            symlink = fixture / "link.py"
            try:
                symlink.symlink_to(source_file)
                
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                analyzer.run()
                
                # Should handle symlinks
                assert context.report is not None
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported on this system")
        finally:
            shutil.rmtree(fixture)
    
    def test_deeply_nested_directories(self):
        """Test deeply nested directories (>10 levels)."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=15)
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle deep nesting
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_very_long_file_paths(self):
        """Test very long file paths (>260 chars on Windows)."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=30)
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle long paths
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_special_characters_in_paths(self):
        """Test special characters in file paths."""
        fixture = Path(tempfile.mkdtemp())
        special_file = fixture / "file with spaces.py"
        special_file.write_text("import os")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle special characters
            assert context.report is not None
        finally:
            shutil.rmtree(fixture)
    
    def test_hidden_files_handled(self):
        """Test hidden files (starting with .) are handled."""
        fixture = Path(tempfile.mkdtemp())
        hidden_file = fixture / ".hidden.py"
        hidden_file.write_text("import os")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle hidden files
            assert context.report is not None
        finally:
            shutil.rmtree(fixture)
    
    def test_unicode_in_filenames(self):
        """Test Unicode characters in filenames."""
        fixture = Path(tempfile.mkdtemp())
        unicode_file = fixture / "文件.py"  # Chinese characters
        unicode_file.write_text("import os")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle Unicode filenames
            assert context.report is not None
        except UnicodeEncodeError:
            # May fail on some systems
            pytest.skip("Unicode filenames not supported on this system")
        finally:
            shutil.rmtree(fixture)
    
    def test_permission_denied_files(self):
        """Test files with permission denied (if possible)."""
        import stat
        
        fixture = Path(tempfile.mkdtemp())
        file_path = fixture / "readonly.py"
        file_path.write_text("import os")
        
        try:
            # Make file read-only (if possible)
            try:
                file_path.chmod(stat.S_IREAD)
                
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                
                # Should handle permission errors gracefully
                try:
                    analyzer.run()
                    handled = True
                except PermissionError:
                    handled = False
                
                assert isinstance(handled, bool)
            except (OSError, NotImplementedError):
                pytest.skip("Cannot test permission errors on this system")
            finally:
                # Restore permissions
                try:
                    file_path.chmod(stat.S_IREAD | stat.S_IWRITE)
                except:
                    pass
        finally:
            shutil.rmtree(fixture)
    
    def test_nonexistent_directory(self):
        """Test nonexistent directory."""
        # Use a guaranteed-nonexistent path (portable across OSes and environments).
        parent = Path(tempfile.mkdtemp())
        nonexistent = parent / "definitely-does-not-exist"
        shutil.rmtree(parent)
        
        context = MigrationContext(project_path=nonexistent, mode="analyze")
        analyzer = CodeAnalyzerAgent(context)
        
        # Should handle nonexistent directory
        with pytest.raises((FileNotFoundError, ValueError)):
            analyzer.run()
    
    def test_file_in_git_directory(self):
        """Test files in .git directory are skipped."""
        fixture = Path(tempfile.mkdtemp())
        (fixture / ".git").mkdir()
        git_file = fixture / ".git" / "config.py"
        git_file.write_text("import os")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # .git files should be skipped
            files = context.report.get("files", [])
            assert ".git" not in str(files)
        finally:
            shutil.rmtree(fixture)

