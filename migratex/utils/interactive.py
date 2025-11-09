"""
Interactive review utilities for CLI
"""

import click
from typing import Literal


def prompt_pattern_decision(
    pattern_id: str,
    file_path: str,
    diff_preview: str = ""
) -> Literal['a', 's', 'e', 'o']:
    """
    Prompt user for pattern decision in review mode.
    Uses click.prompt for consistent CLI experience.
    
    Returns:
        'a' - Accept for this pattern (auto-apply to all similar)
        's' - Skip this pattern
        'e' - Edit manually
        'o' - Only this file (don't auto-apply to others)
    """
    prompt_text = f"""
Pattern: {pattern_id}
File: {file_path}
"""
    
    if diff_preview:
        prompt_text += f"\nDiff preview:\n{diff_preview}\n"
    
    prompt_text += """
[a]ccept for this pattern (auto-apply to all similar)
[s]kip this pattern
[e]dit manually
[o]nly this file (don't auto-apply to others)

Choice"""
    
    choice = click.prompt(
        prompt_text,
        type=click.Choice(['a', 's', 'e', 'o'], case_sensitive=False),
        default='s',
        show_choices=False
    )
    
    return choice.lower()


def prompt_file_decision(
    file_path: str,
    changes_summary: str
) -> Literal['y', 'n', 'e']:
    """
    Prompt user for file-level decision in review mode.
    
    Returns:
        'y' - Yes, apply all changes in this file
        'n' - No, skip this file
        'e' - Edit manually
    """
    prompt_text = f"""
File: {file_path}
Changes: {changes_summary}

[y]es - Apply all changes
[n]o - Skip this file
[e]dit - Edit manually

Choice"""
    
    choice = click.prompt(
        prompt_text,
        type=click.Choice(['y', 'n', 'e'], case_sensitive=False),
        default='n',
        show_choices=False
    )
    
    return choice.lower()

