"""
Utility modules for migration tool
"""

from migratex.utils.interactive import prompt_pattern_decision, prompt_file_decision
from migratex.utils.error_recovery import ErrorRecovery
from migratex.utils.file_ops import copy_project_structure
from migratex.utils.outlier_prompts import prompt_outlier_confirmation, prompt_outlier_file_decision
from migratex.utils.git_ops import (
    is_git_repo,
    get_git_root,
    get_current_branch,
    branch_exists,
    create_migration_branch,
    show_git_diff,
    get_git_status,
    has_uncommitted_changes,
    stash_changes,
    restore_stash
)

__all__ = [
    "prompt_pattern_decision",
    "prompt_file_decision",
    "ErrorRecovery",
    "copy_project_structure",
    "prompt_outlier_confirmation",
    "prompt_outlier_file_decision",
    "is_git_repo",
    "get_git_root",
    "get_current_branch",
    "branch_exists",
    "create_migration_branch",
    "show_git_diff",
    "get_git_status",
    "has_uncommitted_changes",
    "stash_changes",
    "restore_stash"
]
