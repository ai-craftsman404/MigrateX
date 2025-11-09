"""
Outlier-specific user prompts for interactive review
"""

import click
from typing import Literal, Dict, Any


def prompt_outlier_confirmation(outlier_report: Dict[str, Any]) -> Literal['proceed_cautious', 'proceed_review', 'expert_mode', 'abort']:
    """
    Prompt user when outlier codebase detected.
    
    Returns:
        'proceed_cautious' - Proceed with conservative approach
        'proceed_review' - Proceed but force review mode
        'expert_mode' - Generate report only, no transformation
        'abort' - Abort migration
    """
    # Check if running in non-interactive mode (e.g., tests)
    import os
    if os.getenv('MIGRATEX_NON_INTERACTIVE', '').lower() in ('1', 'true', 'yes'):
        # Default to cautious mode in non-interactive mode
        return 'proceed_cautious'
    
    outlier_types = ', '.join(outlier_report.get('outlier_types', []))
    risk_level = outlier_report.get('risk_level', 'unknown')
    confidence = outlier_report.get('confidence', 0.0)
    risks = outlier_report.get('risks', [])
    recommendations = outlier_report.get('recommendations', [])
    
    prompt_text = f"""
⚠️  OUTLIER CODEBASE DETECTED

The codebase has unusual characteristics that may affect migration:

Outlier Types: {outlier_types}
Risk Level: {risk_level.upper()}
Confidence: {confidence:.0%}

Risks:
{chr(10).join(f'  - {risk}' for risk in risks[:5])}
{f'  ... and {len(risks) - 5} more' if len(risks) > 5 else ''}

Recommendations:
{chr(10).join(f'  - {rec}' for rec in recommendations[:5])}
{f'  ... and {len(recommendations) - 5} more' if len(recommendations) > 5 else ''}

How would you like to proceed?

[c]autious - Proceed with conservative approach (recommended)
[r]eview - Proceed but force review mode for all changes
[e]xpert - Generate analysis report only, no transformation
[a]bort - Abort migration

Choice"""
    
    try:
        choice = click.prompt(
            prompt_text,
            type=click.Choice(['c', 'r', 'e', 'a'], case_sensitive=False),
            default='c'
        )
    except (OSError, EOFError):
        # Handle non-interactive environments (e.g., tests)
        return 'proceed_cautious'
    
    return {
        'c': 'proceed_cautious',
        'r': 'proceed_review',
        'e': 'expert_mode',
        'a': 'abort'
    }[choice.lower()]


def prompt_outlier_file_decision(
    file_path: str,
    outlier_reasons: list[str],
    changes_summary: str
) -> Literal['yes', 'no', 'review', 'abort']:
    """
    Prompt user for file-level decision when file is outlier.
    
    Returns:
        'yes' - Proceed with transformation
        'no' - Skip this file
        'review' - Show detailed diff and ask again
        'abort' - Abort migration
    """
    # Check if running in non-interactive mode (e.g., tests)
    import os
    if os.getenv('MIGRATEX_NON_INTERACTIVE', '').lower() in ('1', 'true', 'yes'):
        # Default to 'no' (skip) in non-interactive mode for safety
        return 'no'
    
    prompt_text = f"""
⚠️  OUTLIER FILE DETECTED

File: {file_path}

Outlier Characteristics:
{chr(10).join(f'  - {reason}' for reason in outlier_reasons[:5])}

Proposed Changes: {changes_summary}

This file has unusual characteristics that may affect migration safety.

[y]es - Proceed with transformation (risky)
[n]o - Skip this file (safe, default)
[r]eview - Show detailed diff first
[a]bort - Abort entire migration

Choice"""
    
    try:
        choice = click.prompt(
            prompt_text,
            type=click.Choice(['y', 'n', 'r', 'a'], case_sensitive=False),
            default='n'  # Default to safe option
        )
    except (OSError, EOFError):
        # Handle non-interactive environments (e.g., tests)
        return 'no'
    
    return {
        'y': 'yes',
        'n': 'no',
        'r': 'review',
        'a': 'abort'
    }[choice.lower()]

