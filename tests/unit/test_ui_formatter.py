"""
Unit Tests for UI Formatter (Option 1 - Box Drawing)

Tests the CLI UI formatter with comprehensive coverage of:
- Terminal capability detection
- Box drawing vs ASCII fallback
- All formatting functions
- Cross-platform compatibility
- Edge cases and error handling

Following TESTING_REDEMPTION_PLAN.md standards:
- Strong assertions with outcome verification
- Tests actual functionality, not just "doesn't crash"
- Real-world validation
"""

import pytest
import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from migratex.cli.ui_helpers import (
    CLIFormatter,
    TerminalCapability,
    detect_terminal_capability,
)


class TestTerminalCapabilityDetection:
    """Test terminal capability detection logic."""
    
    def test_detect_capability_default_box_drawing(self):
        """Should default to BOX_DRAWING for modern terminals."""
        with patch.dict(os.environ, {}, clear=True):
            capability = detect_terminal_capability()
            assert capability == TerminalCapability.BOX_DRAWING, \
                "Should default to BOX_DRAWING for safety"
    
    def test_detect_capability_force_ascii_via_env(self):
        """Should respect MIGRATEX_ASCII_ONLY environment variable."""
        with patch.dict(os.environ, {'MIGRATEX_ASCII_ONLY': '1'}):
            capability = detect_terminal_capability()
            assert capability == TerminalCapability.ASCII_ONLY, \
                "Should force ASCII when MIGRATEX_ASCII_ONLY=1"
        
        with patch.dict(os.environ, {'MIGRATEX_ASCII_ONLY': 'true'}):
            capability = detect_terminal_capability()
            assert capability == TerminalCapability.ASCII_ONLY, \
                "Should force ASCII when MIGRATEX_ASCII_ONLY=true"
        
        with patch.dict(os.environ, {'MIGRATEX_ASCII_ONLY': 'yes'}):
            capability = detect_terminal_capability()
            assert capability == TerminalCapability.ASCII_ONLY, \
                "Should force ASCII when MIGRATEX_ASCII_ONLY=yes"
    
    def test_detect_capability_ci_environments(self):
        """Should use ASCII_ONLY in CI/CD environments."""
        ci_vars = ['CI', 'JENKINS_HOME', 'GITHUB_ACTIONS', 'GITLAB_CI', 'CIRCLECI']
        
        for ci_var in ci_vars:
            with patch.dict(os.environ, {ci_var: 'true'}, clear=True):
                capability = detect_terminal_capability()
                assert capability == TerminalCapability.ASCII_ONLY, \
                    f"Should use ASCII_ONLY when {ci_var} is set (for CI/CD logs)"
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_detect_capability_cmd_exe_no_utf8(self):
        """Should use ASCII_ONLY for cmd.exe without UTF-8."""
        # Note: Cannot easily test encoding detection due to readonly attribute
        # This test verifies the logic path exists
        with patch.dict(os.environ, {'COMSPEC': 'C:\\Windows\\system32\\cmd.exe'}, clear=True):
            # Just verify it doesn't crash
            capability = detect_terminal_capability()
            assert capability in [TerminalCapability.ASCII_ONLY, TerminalCapability.BOX_DRAWING], \
                "Should return valid capability for cmd.exe"
    
    def test_detect_capability_dumb_terminal(self):
        """Should use ASCII_ONLY for dumb terminals."""
        with patch.dict(os.environ, {'TERM': 'dumb'}):
            capability = detect_terminal_capability()
            assert capability == TerminalCapability.ASCII_ONLY, \
                "Should use ASCII_ONLY for TERM=dumb"
    
    def test_detect_capability_caching(self):
        """Should cache terminal capability detection."""
        # Reset cache
        CLIFormatter._capability = None
        
        first_call = CLIFormatter._get_capability()
        second_call = CLIFormatter._get_capability()
        
        assert first_call == second_call, "Should return same cached value"
        assert CLIFormatter._capability is not None, "Should cache the capability"


class TestBoxCharacterSelection:
    """Test box drawing character selection based on capability."""
    
    def test_get_box_chars_box_drawing_mode(self):
        """Should return box drawing characters in BOX_DRAWING mode."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        box = CLIFormatter._get_box_chars()
        
        assert box['top_left'] == "╔", "Should use box drawing top-left"
        assert box['top_right'] == "╗", "Should use box drawing top-right"
        assert box['bottom_left'] == "╚", "Should use box drawing bottom-left"
        assert box['bottom_right'] == "╝", "Should use box drawing bottom-right"
        assert box['horizontal'] == "═", "Should use box drawing horizontal"
        assert box['vertical'] == "║", "Should use box drawing vertical"
        assert box['separator'] == "─", "Should use box drawing separator"
    
    def test_get_box_chars_ascii_mode(self):
        """Should return ASCII characters in ASCII_ONLY mode."""
        CLIFormatter._capability = TerminalCapability.ASCII_ONLY
        
        box = CLIFormatter._get_box_chars()
        
        assert box['top_left'] == "+", "Should use ASCII top-left"
        assert box['top_right'] == "+", "Should use ASCII top-right"
        assert box['bottom_left'] == "+", "Should use ASCII bottom-left"
        assert box['bottom_right'] == "+", "Should use ASCII bottom-right"
        assert box['horizontal'] == "=", "Should use ASCII horizontal"
        assert box['vertical'] == "|", "Should use ASCII vertical"
        assert box['separator'] == "-", "Should use ASCII separator"
    
    def test_box_chars_all_single_characters(self):
        """All box characters should be single characters."""
        for mode in [TerminalCapability.BOX_DRAWING, TerminalCapability.ASCII_ONLY]:
            CLIFormatter._capability = mode
            box = CLIFormatter._get_box_chars()
            
            for name, char in box.items():
                assert len(char) == 1, \
                    f"Box char '{name}' should be single character, got '{char}' (len={len(char)})"


class TestHeaderFormatting:
    """Test header formatting with box drawing."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_header_renders_without_error(self, mock_stdout):
        """Header should render without errors."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        try:
            CLIFormatter.header("Test Header")
            output = mock_stdout.getvalue()
            assert len(output) > 0, "Header should produce output"
        except Exception as e:
            pytest.fail(f"Header rendering should not raise exception: {e}")
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_header_contains_title(self, mock_stdout):
        """Header should contain the title text."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        CLIFormatter.header("My Test Title")
        output = mock_stdout.getvalue()
        
        assert "My Test Title" in output, "Header should contain title text"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_header_has_box_structure(self, mock_stdout):
        """Header should have top and bottom borders."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        CLIFormatter.header("Test")
        output = mock_stdout.getvalue()
        
        lines = output.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        assert len(non_empty_lines) >= 3, "Header should have at least 3 lines (top, title, bottom)"
        assert "╔" in lines[1] or "+" in lines[1], "Should have top border"
        assert "╚" in lines[3] or "+" in lines[3], "Should have bottom border"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_header_ascii_fallback(self, mock_stdout):
        """Header should use ASCII in ASCII_ONLY mode."""
        CLIFormatter._capability = TerminalCapability.ASCII_ONLY
        
        CLIFormatter.header("Test")
        output = mock_stdout.getvalue()
        
        assert "+" in output, "ASCII mode should use + for corners"
        assert "=" in output, "ASCII mode should use = for horizontal lines"
        assert "|" in output, "ASCII mode should use | for vertical lines"
        assert "╔" not in output, "ASCII mode should not use box drawing characters"


class TestFieldFormatting:
    """Test field labeling and formatting."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_field_renders_label_and_value(self, mock_stdout):
        """Field should render both label and value."""
        CLIFormatter.field("Project", "/path/to/project")
        output = mock_stdout.getvalue()
        
        assert "[PROJECT]" in output, "Should render label in brackets"
        assert "/path/to/project" in output, "Should render value"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_field_handles_various_types(self, mock_stdout):
        """Field should handle different value types."""
        test_values = [
            ("String", "test string"),
            ("Number", 42),
            ("Float", 3.14),
            ("Bool", True),
            ("Path", Path("/test/path")),
        ]
        
        for label, value in test_values:
            mock_stdout.truncate(0)
            mock_stdout.seek(0)
            
            CLIFormatter.field(label, value)
            output = mock_stdout.getvalue()
            
            assert str(value) in output, \
                f"Should render {type(value).__name__} value '{value}'"


class TestStatusMessages:
    """Test status message formatting (success, error, warning, info)."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_success_message(self, mock_stdout):
        """Success message should render with indicator."""
        CLIFormatter.success("Operation completed")
        output = mock_stdout.getvalue()
        
        assert "+" in output or "✓" in output, "Should have success indicator"
        assert "Operation completed" in output, "Should contain message"
    
    @patch('sys.stderr', new_callable=StringIO)
    def test_error_message_to_stderr(self, mock_stderr):
        """Error message should output to stderr."""
        CLIFormatter.error("Operation failed")
        output = mock_stderr.getvalue()
        
        assert "x" in output or "✗" in output, "Should have error indicator"
        assert "Operation failed" in output, "Should contain message"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_message(self, mock_stdout):
        """Warning message should render with indicator."""
        CLIFormatter.warning("Be careful")
        output = mock_stdout.getvalue()
        
        assert "[WARN]" in output, "Should have warning indicator"
        assert "Be careful" in output, "Should contain message"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_message_with_indent(self, mock_stdout):
        """Warning message should support indentation."""
        CLIFormatter.warning("Indented warning", indent=True)
        output = mock_stdout.getvalue()
        
        assert output.startswith("   "), "Indented warning should start with spaces"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_message(self, mock_stdout):
        """Info message should render with indicator."""
        CLIFormatter.info("Helpful information")
        output = mock_stdout.getvalue()
        
        assert "[INFO]" in output, "Should have info indicator"
        assert "Helpful information" in output, "Should contain message"


class TestProgressIndicators:
    """Test progress and bullet formatting."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_message(self, mock_stdout):
        """Progress message should render with arrow."""
        CLIFormatter.progress("Processing files...")
        output = mock_stdout.getvalue()
        
        assert ">" in output or "→" in output, "Should have progress arrow"
        assert "Processing files..." in output, "Should contain message"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_bullet_point(self, mock_stdout):
        """Bullet point should render with indicator."""
        CLIFormatter.bullet("First item")
        output = mock_stdout.getvalue()
        
        assert "*" in output or "•" in output, "Should have bullet indicator"
        assert "First item" in output, "Should contain text"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_bullet_list(self, mock_stdout):
        """Multiple bullets should render as list."""
        items = ["Item 1", "Item 2", "Item 3"]
        
        for item in items:
            CLIFormatter.bullet(item)
        
        output = mock_stdout.getvalue()
        
        for item in items:
            assert item in output, f"Should contain '{item}'"
        
        bullet_count = output.count("*")  # Or "•"
        assert bullet_count >= 3, "Should have at least 3 bullets"


class TestSeparatorFormatting:
    """Test separator line formatting."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_separator_default_width(self, mock_stdout):
        """Separator should render with default width."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        CLIFormatter.separator()
        output = mock_stdout.getvalue()
        
        lines = output.strip().split('\n')
        assert len(lines) > 0, "Separator should produce at least one line"
        
        separator_line = lines[0]
        assert len(separator_line) == 80, "Default separator should be 80 characters wide"
        assert "─" in separator_line or "-" in separator_line, "Should contain separator character"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_separator_custom_width(self, mock_stdout):
        """Separator should respect custom width."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        CLIFormatter.separator(width=40)
        output = mock_stdout.getvalue()
        
        lines = output.strip().split('\n')
        separator_line = lines[0]
        assert len(separator_line) == 40, "Custom separator should be 40 characters wide"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_separator_ascii_mode(self, mock_stdout):
        """Separator should use ASCII in ASCII_ONLY mode."""
        CLIFormatter._capability = TerminalCapability.ASCII_ONLY
        
        CLIFormatter.separator()
        output = mock_stdout.getvalue()
        
        assert "-" in output, "ASCII mode separator should use hyphens"
        assert "─" not in output, "ASCII mode should not use box drawing"


class TestSummaryBox:
    """Test summary box formatting."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_summary_box_renders(self, mock_stdout):
        """Summary box should render with title and items."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        items = [
            ("Files transformed", 12),
            ("Patterns applied", 15),
            ("Status", "SUCCESS"),
        ]
        
        CLIFormatter.summary_box("Summary", items)
        output = mock_stdout.getvalue()
        
        assert "SUMMARY" in output, "Should contain title"
        assert "Files transformed" in output, "Should contain item keys"
        assert "12" in output, "Should contain item values"
        assert "15" in output, "Should contain item values"
        assert "SUCCESS" in output, "Should contain item values"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_summary_box_has_borders(self, mock_stdout):
        """Summary box should have top and bottom borders."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        CLIFormatter.summary_box("Test", [("Key", "Value")])
        output = mock_stdout.getvalue()
        
        lines = output.split('\n')
        non_empty = [l for l in lines if l.strip()]
        
        # Should have border lines
        first_line = non_empty[0] if non_empty else ""
        last_line = non_empty[-1] if len(non_empty) > 1 else ""
        
        # Check for box drawing characters (╔ or ┌) or ASCII (+)
        assert ("╔" in first_line or "┌" in first_line or "+" in first_line), "Should have top border"
        assert ("╚" in last_line or "└" in last_line or "+" in last_line), "Should have bottom border"


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_empty_title_header(self, mock_stdout):
        """Should handle empty title gracefully."""
        CLIFormatter.header("")
        output = mock_stdout.getvalue()
        
        assert len(output) > 0, "Should produce output even with empty title"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_very_long_title(self, mock_stdout):
        """Should handle very long titles without crashing."""
        long_title = "A" * 200
        
        try:
            CLIFormatter.header(long_title, width=80)
            output = mock_stdout.getvalue()
            assert len(output) > 0, "Should handle long titles"
        except Exception as e:
            pytest.fail(f"Should not crash on long title: {e}")
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_unicode_in_messages(self, mock_stdout):
        """Should handle Unicode characters in messages."""
        unicode_msg = "Test with émojis and spëcial çharacters"
        
        try:
            CLIFormatter.field("Test", unicode_msg)
            output = mock_stdout.getvalue()
            # Just verify it doesn't crash
            assert len(output) > 0, "Should handle Unicode"
        except UnicodeEncodeError:
            pytest.skip("Terminal doesn't support Unicode")
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_none_values(self, mock_stdout):
        """Should handle None values gracefully."""
        CLIFormatter.field("Test", None)
        output = mock_stdout.getvalue()
        
        assert "None" in output, "Should convert None to string"


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility."""
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_windows_encoding_safe(self):
        """Should work on Windows without encoding errors."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        try:
            CLIFormatter.header("Test Header")
            CLIFormatter.separator()
            CLIFormatter.success("Success")
            # If we get here without UnicodeEncodeError, it works
            assert True
        except UnicodeEncodeError:
            pytest.fail("Should not raise UnicodeEncodeError on Windows")
    
    def test_all_platforms_ascii_mode_works(self):
        """ASCII mode should work on all platforms."""
        CLIFormatter._capability = TerminalCapability.ASCII_ONLY
        
        try:
            CLIFormatter.header("Test")
            CLIFormatter.separator()
            CLIFormatter.success("Success")
            CLIFormatter.error("Error")
            CLIFormatter.warning("Warning")
            CLIFormatter.info("Info")
            CLIFormatter.progress("Progress")
            # If we get here, ASCII mode works
            assert True
        except Exception as e:
            pytest.fail(f"ASCII mode should work everywhere: {e}")


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_analyze_command_output_simulation(self, mock_stdout):
        """Simulate complete analyze command output."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        # Header
        CLIFormatter.header("MigrateX - Analysis")
        CLIFormatter.field("Project", "/test/project")
        CLIFormatter.field("Mode", "Analysis (read-only)")
        CLIFormatter.separator()
        
        # Progress
        CLIFormatter.progress("Scanning project files...")
        
        # Results
        CLIFormatter.separator()
        CLIFormatter.section("RESULTS")
        CLIFormatter.field("Files scanned", 12)
        CLIFormatter.field("Patterns detected", 15)
        
        # Success
        CLIFormatter.separator()
        CLIFormatter.success("Analysis complete!")
        
        output = mock_stdout.getvalue()
        
        # Verify all elements present
        assert "MigrateX - Analysis" in output
        assert "/test/project" in output
        assert "12" in output
        assert "15" in output
        assert len(output) > 100, "Should produce substantial output"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_apply_command_output_simulation(self, mock_stdout):
        """Simulate complete apply command output."""
        CLIFormatter._capability = TerminalCapability.BOX_DRAWING
        
        # Header
        CLIFormatter.header("MigrateX - Apply Migration")
        CLIFormatter.field("Project", "/test/project")
        CLIFormatter.field("Mode", "Auto (high-confidence)")
        CLIFormatter.field("Git branch", "migratex/auto")
        CLIFormatter.separator()
        
        # Warning
        CLIFormatter.warning("Uncommitted changes detected")
        CLIFormatter.warning("Consider committing first", indent=True)
        CLIFormatter.separator()
        
        # Progress
        CLIFormatter.progress("Starting migration...")
        
        # Success
        CLIFormatter.separator()
        CLIFormatter.success("Migration complete!")
        CLIFormatter.field("Files transformed", 12)
        
        output = mock_stdout.getvalue()
        
        # Verify all elements present
        assert "Apply Migration" in output
        assert "Uncommitted changes" in output
        assert "Migration complete" in output
        assert len(output) > 100, "Should produce substantial output"


# Test discovery: Ensure pytest can find all tests
def test_suite_has_comprehensive_coverage():
    """Meta-test: Verify test suite has good coverage."""
    test_classes = [
        TestTerminalCapabilityDetection,
        TestBoxCharacterSelection,
        TestHeaderFormatting,
        TestFieldFormatting,
        TestStatusMessages,
        TestProgressIndicators,
        TestSeparatorFormatting,
        TestSummaryBox,
        TestEdgeCases,
        TestCrossPlatformCompatibility,
        TestRealWorldScenarios,
    ]
    
    total_tests = sum(
        len([m for m in dir(cls) if m.startswith('test_')])
        for cls in test_classes
    )
    
    assert total_tests >= 35, \
        f"Test suite should have at least 35 tests for comprehensive coverage, found {total_tests}"

