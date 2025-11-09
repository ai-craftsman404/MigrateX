"""
CLI UI Helpers - Enhanced output formatting (Option 1: Box Drawing)

Provides consistent, readable, and visually appealing CLI output.
Windows-compatible with automatic ASCII fallback for maximum compatibility.

Design: Option 1 - Clean & Professional
- Box drawing for structure (╔═╗ style)
- ASCII fallback for old terminals
- No emojis (enterprise-safe)
- Cross-platform tested
"""

import click
import sys
import os
from typing import Optional, List, Dict, Any
from enum import Enum


class TerminalCapability(Enum):
    """Terminal capability levels for output formatting."""
    ASCII_ONLY = 1      # cmd.exe, CI/CD, old terminals
    BOX_DRAWING = 2     # PowerShell 5.1+, modern terminals (DEFAULT)


def detect_terminal_capability() -> TerminalCapability:
    """
    Detect terminal capabilities and return appropriate level.
    Defaults to BOX_DRAWING for safety, falls back to ASCII if needed.
    
    Returns:
        TerminalCapability: Detected capability level
    """
    # Force ASCII mode via environment variable (for CI/CD)
    if os.environ.get('MIGRATEX_ASCII_ONLY', '').lower() in ('1', 'true', 'yes'):
        return TerminalCapability.ASCII_ONLY
    
    # Check if running in CI/CD (always use ASCII for logs)
    ci_indicators = ['CI', 'JENKINS_HOME', 'GITHUB_ACTIONS', 'GITLAB_CI', 'CIRCLECI']
    if any(os.environ.get(key) for key in ci_indicators):
        return TerminalCapability.ASCII_ONLY
    
    # Check for cmd.exe (no box drawing support)
    if sys.platform == 'win32':
        # Check if it's cmd.exe (PROMPT contains $P$G by default)
        if 'cmd.exe' in os.environ.get('COMSPEC', '').lower():
            # If no UTF-8 support, use ASCII
            try:
                if sys.stdout.encoding.lower() not in ['utf-8', 'utf8']:
                    return TerminalCapability.ASCII_ONLY
            except:
                return TerminalCapability.ASCII_ONLY
    
    # Check for dumb terminal
    if os.environ.get('TERM') == 'dumb':
        return TerminalCapability.ASCII_ONLY
    
    # Default to BOX_DRAWING (safe for PowerShell 5.1+, VSCode, modern terminals)
    return TerminalCapability.BOX_DRAWING


class CLIFormatter:
    """
    Formats CLI output with colors, boxes, and visual hierarchy.
    Option 1 style: Box drawing with ASCII fallback.
    """
    
    # Terminal capability (set on first use)
    _capability: Optional[TerminalCapability] = None
    
    # Box drawing characters (UTF-8, PowerShell 5.1+ compatible)
    BOX_TOP_LEFT = "╔"
    BOX_TOP_RIGHT = "╗"
    BOX_BOTTOM_LEFT = "╚"
    BOX_BOTTOM_RIGHT = "╝"
    BOX_HORIZONTAL = "═"
    BOX_VERTICAL = "║"
    SEPARATOR = "─"
    
    # ASCII fallback characters
    ASCII_BOX_TOP_LEFT = "+"
    ASCII_BOX_TOP_RIGHT = "+"
    ASCII_BOX_BOTTOM_LEFT = "+"
    ASCII_BOX_BOTTOM_RIGHT = "+"
    ASCII_BOX_HORIZONTAL = "="
    ASCII_BOX_VERTICAL = "|"
    ASCII_SEPARATOR = "-"
    
    # Status indicators (text only, no emojis)
    SUCCESS = "[OK]"
    ERROR = "[ERROR]"
    WARNING = "[WARN]"
    INFO = "[INFO]"
    PROGRESS = "[...]"
    
    # Visual indicators (safe symbols)
    CHECK = "+"      # Success indicator (ASCII-safe)
    CROSS = "x"      # Error indicator (ASCII-safe)
    ARROW = ">"      # Progress indicator (ASCII-safe)
    BULLET = "*"     # Bullet point (ASCII-safe)
    
    # Colors (Click built-in, cross-platform)
    COLOR_SUCCESS = "green"
    COLOR_ERROR = "red"
    COLOR_WARNING = "yellow"
    COLOR_INFO = "cyan"
    COLOR_HEADER = "bright_white"
    COLOR_DIM = "bright_black"
    
    @classmethod
    def _get_capability(cls) -> TerminalCapability:
        """Get or detect terminal capability (cached)."""
        if cls._capability is None:
            cls._capability = detect_terminal_capability()
        return cls._capability
    
    @classmethod
    def _get_box_chars(cls) -> Dict[str, str]:
        """Get appropriate box drawing characters based on terminal capability."""
        if cls._get_capability() == TerminalCapability.ASCII_ONLY:
            return {
                'top_left': cls.ASCII_BOX_TOP_LEFT,
                'top_right': cls.ASCII_BOX_TOP_RIGHT,
                'bottom_left': cls.ASCII_BOX_BOTTOM_LEFT,
                'bottom_right': cls.ASCII_BOX_BOTTOM_RIGHT,
                'horizontal': cls.ASCII_BOX_HORIZONTAL,
                'vertical': cls.ASCII_BOX_VERTICAL,
                'separator': cls.ASCII_SEPARATOR,
            }
        else:
            return {
                'top_left': cls.BOX_TOP_LEFT,
                'top_right': cls.BOX_TOP_RIGHT,
                'bottom_left': cls.BOX_BOTTOM_LEFT,
                'bottom_right': cls.BOX_BOTTOM_RIGHT,
                'horizontal': cls.BOX_HORIZONTAL,
                'vertical': cls.BOX_VERTICAL,
                'separator': cls.SEPARATOR,
            }
    
    @classmethod
    def header(cls, title: str, width: int = 80) -> None:
        """
        Print a boxed header (Option 1 style).
        
        Example (Box Drawing):
            ╔══════════════════════════════════════╗
            ║         MigrateX Analysis            ║
            ╚══════════════════════════════════════╝
        
        Example (ASCII Fallback):
            +======================================+
            |         MigrateX Analysis            |
            +======================================+
        """
        box = cls._get_box_chars()
        inner_width = width - 2
        padding = (inner_width - len(title)) // 2
        padded_title = " " * padding + title + " " * (inner_width - padding - len(title))
        
        click.echo()
        click.secho(
            box['top_left'] + box['horizontal'] * (width - 2) + box['top_right'],
            fg=cls.COLOR_HEADER, bold=True
        )
        click.secho(
            box['vertical'] + padded_title + box['vertical'],
            fg=cls.COLOR_HEADER, bold=True
        )
        click.secho(
            box['bottom_left'] + box['horizontal'] * (width - 2) + box['bottom_right'],
            fg=cls.COLOR_HEADER, bold=True
        )
        click.echo()
    
    @classmethod
    def separator(cls, width: int = 80) -> None:
        """Print a horizontal separator line."""
        box = cls._get_box_chars()
        click.secho(box['separator'] * width, fg=cls.COLOR_DIM)
    
    @classmethod
    def section(cls, title: str) -> None:
        """Print a section header."""
        click.echo()
        click.secho(f"> {title.upper()}", fg=cls.COLOR_INFO, bold=True)
    
    @classmethod
    def field(cls, label: str, value: Any, color: Optional[str] = None) -> None:
        """
        Print a labeled field.
        
        Example: [LABEL] Value
        """
        label_styled = click.style(f"[{label.upper()}]", fg=cls.COLOR_INFO, bold=True)
        value_str = str(value)
        if color:
            value_str = click.style(value_str, fg=color)
        click.echo(f"{label_styled}  {value_str}")
    
    @classmethod
    def success(cls, message: str) -> None:
        """Print a success message."""
        click.secho(f"{cls.CHECK} {message}", fg=cls.COLOR_SUCCESS, bold=True)
    
    @classmethod
    def error(cls, message: str) -> None:
        """Print an error message."""
        click.secho(f"{cls.CROSS} {message}", fg=cls.COLOR_ERROR, bold=True, err=True)
    
    @classmethod
    def warning(cls, message: str, indent: bool = False) -> None:
        """Print a warning message."""
        prefix = "   " if indent else ""
        click.secho(f"{prefix}{cls.WARNING}  {message}", fg=cls.COLOR_WARNING, bold=True)
    
    @classmethod
    def info(cls, message: str) -> None:
        """Print an info message."""
        click.secho(f"{cls.INFO}  {message}", fg=cls.COLOR_INFO)
    
    @classmethod
    def bullet(cls, message: str, color: Optional[str] = None) -> None:
        """Print a bullet point."""
        styled_msg = click.style(message, fg=color) if color else message
        click.echo(f"  {cls.BULLET} {styled_msg}")
    
    @classmethod
    def key_value(cls, key: str, value: Any, indent: int = 0) -> None:
        """Print a key-value pair."""
        prefix = " " * indent
        key_styled = click.style(f"{key}:", fg=cls.COLOR_DIM)
        click.echo(f"{prefix}{key_styled} {value}")
    
    @classmethod
    def progress(cls, message: str) -> None:
        """Print a progress message."""
        click.secho(f"{cls.ARROW} {message}", fg=cls.COLOR_INFO)
    
    @classmethod
    def summary_box(cls, title: str, items: List[tuple], width: int = 80) -> None:
        """
        Print a summary box with key-value pairs (Option 1 style).
        
        Example (Box Drawing):
            ┌─ SUMMARY ──────────────────────────┐
            │ Files transformed: 12              │
            │ Patterns applied:  15              │
            │ Status:           SUCCESS          │
            └────────────────────────────────────┘
        
        Example (ASCII Fallback):
            +- SUMMARY -------------+
            | Files transformed: 12  |
            | Patterns applied:  15  |
            | Status:           SUCCESS |
            +------------------------+
        """
        box = cls._get_box_chars()
        click.echo()
        
        # Top border with title
        title_text = f"{box['horizontal']} {title.upper()} "
        remaining = width - len(title_text) - 2
        title_line = box['top_left'] + title_text + box['horizontal'] * remaining + box['top_right']
        click.secho(title_line, fg=cls.COLOR_INFO, bold=True)
        
        # Content
        for key, value in items:
            # Calculate padding for alignment
            max_key_len = max(len(k) for k, v in items)
            padded_key = f"{key}:".ljust(max_key_len + 1)
            
            content_line = f"{box['vertical']} {padded_key} {value}"
            padding = width - len(content_line) - 1
            click.echo(content_line + " " * padding + box['vertical'])
        
        # Bottom border
        click.secho(box['bottom_left'] + box['horizontal'] * (width - 2) + box['bottom_right'], 
                   fg=cls.COLOR_INFO, bold=True)
        click.echo()
    
    @classmethod
    def table(cls, headers: List[str], rows: List[List[str]], widths: Optional[List[int]] = None) -> None:
        """Print a simple table."""
        if not widths:
            # Auto-calculate widths
            widths = [
                max(len(str(headers[i])), max(len(str(row[i])) for row in rows))
                for i in range(len(headers))
            ]
        
        # Header
        header_line = "  ".join(
            click.style(h.ljust(w), fg=cls.COLOR_INFO, bold=True)
            for h, w in zip(headers, widths)
        )
        click.echo(header_line)
        click.secho("─" * (sum(widths) + 2 * (len(widths) - 1)), fg=cls.COLOR_DIM)
        
        # Rows
        for row in rows:
            row_line = "  ".join(
                str(cell).ljust(width)
                for cell, width in zip(row, widths)
            )
            click.echo(row_line)
    
    @classmethod
    def status_summary(cls, 
                       success_count: int, 
                       error_count: int, 
                       warning_count: int,
                       total: int) -> None:
        """Print a status summary with counts."""
        click.echo()
        click.secho("STATUS SUMMARY:", fg=cls.COLOR_HEADER, bold=True)
        
        if success_count > 0:
            cls.bullet(f"{success_count} successful", cls.COLOR_SUCCESS)
        if error_count > 0:
            cls.bullet(f"{error_count} errors", cls.COLOR_ERROR)
        if warning_count > 0:
            cls.bullet(f"{warning_count} warnings", cls.COLOR_WARNING)
        
        # Overall status
        click.echo()
        if error_count == 0:
            cls.success(f"Completed successfully ({success_count}/{total})")
        else:
            cls.error(f"Completed with errors ({total - error_count}/{total} succeeded)")
    
    @classmethod
    def outlier_warning_box(cls, outlier_report: Dict[str, Any]) -> None:
        """Print a prominent outlier warning (Option 1 style)."""
        box = cls._get_box_chars()
        width = 80
        
        click.echo()
        click.echo()
        # Warning box
        click.secho(box['top_left'] + box['horizontal'] * (width - 2) + box['top_right'], 
                   fg=cls.COLOR_WARNING, bold=True)
        warning_text = f"{cls.WARNING}  OUTLIER CODEBASE DETECTED  {cls.WARNING}"
        padding = (width - 2 - len(warning_text)) // 2
        padded_warning = " " * padding + warning_text + " " * (width - 2 - padding - len(warning_text))
        click.secho(box['vertical'] + padded_warning + box['vertical'], 
                   fg=cls.COLOR_WARNING, bold=True)
        click.secho(box['bottom_left'] + box['horizontal'] * (width - 2) + box['bottom_right'], 
                   fg=cls.COLOR_WARNING, bold=True)
        click.echo()
        
        risk_level = outlier_report.get('risk_level', 'unknown').upper()
        confidence = outlier_report.get('confidence', 0.0)
        
        cls.field("Risk Level", risk_level, cls.COLOR_WARNING)
        cls.field("Confidence", f"{confidence:.0%}", cls.COLOR_WARNING)
        cls.field("Outlier Types", ", ".join(outlier_report.get('outlier_types', [])))
        
        risks = outlier_report.get('risks', [])
        if risks:
            click.echo()
            click.secho("Key Risks:", fg=cls.COLOR_WARNING, bold=True)
            for risk in risks[:3]:
                cls.bullet(risk, cls.COLOR_WARNING)
            if len(risks) > 3:
                cls.warning(f"... and {len(risks) - 3} more (see report)", indent=True)
        
        recommendations = outlier_report.get('recommendations', [])
        if recommendations:
            click.echo()
            click.secho("Recommendations:", fg=cls.COLOR_INFO, bold=True)
            for rec in recommendations[:3]:
                cls.bullet(rec)
            if len(recommendations) > 3:
                cls.info(f"... and {len(recommendations) - 3} more (see report)")
        
        click.echo()
        cls.warning("Review 'outlier_report' section in analysis report for full details")
        click.echo()


# Convenience functions
def print_header(title: str, width: int = 80) -> None:
    """Print a formatted header."""
    CLIFormatter.header(title, width)


def print_section(title: str) -> None:
    """Print a section header."""
    CLIFormatter.section(title)


def print_separator(width: int = 80) -> None:
    """Print a separator line."""
    CLIFormatter.separator(width)


def print_field(label: str, value: Any, color: Optional[str] = None) -> None:
    """Print a labeled field."""
    CLIFormatter.field(label, value, color)


def print_success(message: str) -> None:
    """Print a success message."""
    CLIFormatter.success(message)


def print_error(message: str) -> None:
    """Print an error message."""
    CLIFormatter.error(message)


def print_warning(message: str, indent: bool = False) -> None:
    """Print a warning message."""
    CLIFormatter.warning(message, indent)


def print_progress(message: str) -> None:
    """Print a progress message."""
    CLIFormatter.progress(message)

