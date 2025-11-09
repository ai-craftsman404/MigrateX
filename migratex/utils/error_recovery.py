"""
Error recovery and retry logic
"""

from typing import Dict, List, Any
from pathlib import Path


class ErrorRecovery:
    """
    Handles error recovery for failed files.
    Policy: No auto-retry - manual review required.
    """
    
    @staticmethod
    def record_failed_file(
        context,
        file_path: Path,
        error: str,
        pattern_id: str = None
    ):
        """
        Record a failed file in checkpoint.
        No auto-retry - user must review and fix manually.
        """
        failure_record = {
            "file": str(file_path),
            "error": str(error),
            "pattern_id": pattern_id,
            "requires_manual_review": True,
            "auto_retry": False  # Explicitly no auto-retry
        }
        
        context.failed_files.append(failure_record)
        
        if context.verbose:
            print(f"✗ Failed: {file_path}")
            print(f"  Error: {error}")
            print(f"  Requires manual review")
    
    @staticmethod
    def get_failed_files_summary(context) -> Dict[str, Any]:
        """
        Get summary of failed files for user review.
        """
        return {
            "total_failed": len(context.failed_files),
            "failed_files": context.failed_files,
            "recommendation": "Review failed files manually. Fix issues and re-run migration."
        }
    
    @staticmethod
    def should_retry(context, file_path: Path) -> bool:
        """
        Check if file should be retried.
        Policy: Always returns False - no auto-retry.
        """
        return False  # Explicit no-auto-retry policy

