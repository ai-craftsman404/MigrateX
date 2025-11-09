"""
Core context module
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional
from migratex.patterns.cache import PatternCache
from migratex.patterns.library import PatternLibrary


@dataclass
class MigrationContext:
    """
    Shared state object for migration agents.
    All agents read/write through this context.
    """
    
    # Project paths
    project_path: Path
    output_dir: Optional[Path] = None  # If set, write migrated code here instead of in-place
    
    # Mode configuration
    mode: str = "analyze"  # "analyze", "auto", "review"
    verbose: bool = False
    
    # File paths
    report_path: Optional[Path] = None
    pattern_cache_path: Optional[Path] = None
    
    # Review mode settings
    remember_decisions: bool = False
    show_diff: bool = False
    review_granularity: str = "pattern"  # "pattern", "file", "none"
    
    # Error handling
    error_policy: str = "continue"  # "continue", "stop"
    
    # Outlier handling
    outlier_mode: Optional[str] = None  # "cautious", "review", "expert", None
    interactive: bool = True  # Whether to prompt user for decisions
    
    # Git integration (default enabled - primary strategy)
    use_git_branch: bool = True  # Default: True - use git branch workflow
    git_branch_name: str = "migratex/migrate-to-maf"  # Default branch name
    auto_create_branch: bool = True  # Default: True - create branch automatically
    show_git_diff: bool = True  # Default: True - show git diff after migration
    
    # Runtime state
    report: Dict[str, Any] = field(default_factory=dict)
    pattern_cache: Optional[PatternCache] = None
    pattern_library: Optional[PatternLibrary] = None
    
    # Git runtime state
    git_root: Optional[Path] = None  # Git root directory (detected at runtime)
    original_branch: Optional[str] = None  # Original branch before migration (for restoration)
    
    # Migration results
    updated_files: List[str] = field(default_factory=list)
    failed_files: List[Dict[str, Any]] = field(default_factory=list)
    patterns_applied: List[str] = field(default_factory=list)
    
    # Testing results tracker (for acceptance criteria)
    testing_tracker: Any = None
    
    # Current task tracking
    current_task_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize pattern cache and library."""
        from migratex.patterns.cache import PatternCache
        from migratex.patterns.library import PatternLibrary
        from migratex.testing.results_tracker import testing_tracker
        from migratex.utils.git_ops import get_git_root, get_current_branch
        
        if self.pattern_cache_path:
            self.pattern_cache = PatternCache(self.pattern_cache_path)
        else:
            # Default cache location
            cache_path = self.project_path / "pattern-cache.yaml"
            self.pattern_cache = PatternCache(cache_path)
        
        self.pattern_library = PatternLibrary()
        
        # Initialize testing tracker if not provided
        if self.testing_tracker is None:
            self.testing_tracker = testing_tracker
        
        # Detect git repository if git integration is enabled
        if self.use_git_branch:
            self.git_root = get_git_root(self.project_path)
            if self.git_root:
                self.original_branch = get_current_branch(self.project_path)
    
    def get_task_manager(self):
        """Get task manager instance for this context."""
        from migratex.core.task_manager import TaskManager
        return TaskManager(self)
    
    def load_patterns(self):
        """Load relevant patterns based on discovery results."""
        if "patterns" in self.report:
            detected_pattern_ids = [p.get("id") for p in self.report["patterns"]]
            self.pattern_library.load_relevant(detected_pattern_ids)
    
    def get_report(self) -> Dict[str, Any]:
        """Get the analysis report."""
        return self.report
    
    def get_checkpoint(self) -> Dict[str, Any]:
        """Get migration checkpoint/results."""
        return {
            "updated_files": self.updated_files,
            "failed_files": self.failed_files,
            "patterns_applied": self.patterns_applied,
            "total_files": len(self.updated_files) + len(self.failed_files)
        }
    
    def write_summary(self, output_path: Path):
        """Write markdown summary to file."""
        checkpoint = self.get_checkpoint()
        
        summary_lines = [
            "# Migration Summary",
            "",
            f"## Results",
            f"- Files updated: {len(checkpoint['updated_files'])}",
            f"- Files failed: {len(checkpoint['failed_files'])}",
            f"- Patterns applied: {len(checkpoint['patterns_applied'])}",
            "",
            "## Updated Files",
        ]
        
        for file_path in checkpoint["updated_files"]:
            summary_lines.append(f"- {file_path}")
        
        if checkpoint["failed_files"]:
            summary_lines.extend([
                "",
                "## Failed Files",
            ])
            for failure in checkpoint["failed_files"]:
                summary_lines.append(f"- {failure.get('file', 'unknown')}: {failure.get('error', 'unknown error')}")
        
        with open(output_path, "w") as f:
            f.write("\n".join(summary_lines))

