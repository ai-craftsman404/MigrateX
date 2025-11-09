"""
Core orchestration module - Central coordinator
"""

from migratex.core.context import MigrationContext


class Orchestrator:
    """
    Central coordinator for migration agents.
    Uses direct method calls with shared MigrationContext for state.
    """
    
    def __init__(self, context: MigrationContext):
        self.context = context
    
    def _setup_git_branch(self) -> bool:
        """
        Set up git branch for migration (if git integration enabled).
        
        Returns:
            True if branch setup successful or not needed, False on error
        """
        if not self.context.use_git_branch or not self.context.git_root:
            return True  # Git integration disabled or not a git repo
        
        from migratex.utils.git_ops import (
            create_migration_branch,
            has_uncommitted_changes,
            get_current_branch
        )
        
        try:
            # Check for uncommitted changes
            if has_uncommitted_changes(self.context.project_path):
                if self.context.verbose:
                    print("Warning: Uncommitted changes detected. Consider committing or stashing before migration.")
                # Continue anyway - user can handle manually
            
            # Store original branch if not already stored
            if self.context.original_branch is None:
                self.context.original_branch = get_current_branch(self.context.project_path)
            
            # Create/checkout migration branch
            if self.context.auto_create_branch:
                success = create_migration_branch(
                    self.context.project_path,
                    self.context.git_branch_name
                )
                if success and self.context.verbose:
                    print(f"Created/checked out branch: {self.context.git_branch_name}")
                return success
            
            return True
        except Exception as e:
            if self.context.verbose:
                print(f"Warning: Git branch setup failed: {e}")
            # Continue without git branch - graceful fallback
            return False
    
    def _show_git_diff(self) -> None:
        """
        Show git diff after migration (if git integration enabled).
        """
        if not self.context.show_git_diff or not self.context.git_root:
            return  # Git diff disabled or not a git repo
        
        from migratex.utils.git_ops import show_git_diff
        
        try:
            diff_output = show_git_diff(self.context.project_path)
            if diff_output:
                print("\n" + "="*60)
                print("Git Diff - Changes Made:")
                print("="*60)
                print(diff_output)
                print("="*60)
            elif self.context.verbose:
                print("No changes detected in git diff.")
        except Exception as e:
            if self.context.verbose:
                print(f"Warning: Could not show git diff: {e}")
    
    def run_analysis(self):
        """
        Run the analysis phase (read-only discovery).
        """
        from migratex.agents.code_analyzer import CodeAnalyzerAgent
        
        # Run code analyzer agent
        analyzer = CodeAnalyzerAgent(self.context)
        analyzer.run()
    
    def run_apply_auto(self):
        """
        Run the apply phase in auto mode (high-confidence transformations).
        """
        from migratex.agents.refactorer import RefactorerAgent
        from migratex.agents.codemod_designer import CodemodDesignerAgent
        from migratex.utils.file_ops import copy_project_structure
        
        # Set up git branch if enabled (primary strategy)
        self._setup_git_branch()
        
        # If output_dir is set, copy project structure first
        if self.context.output_dir:
            copy_project_structure(self.context.project_path, self.context.output_dir)
            if self.context.verbose:
                print(f"Copied project structure to: {self.context.output_dir}")
        
        # Load relevant patterns
        self.context.load_patterns()
        
        # Run codemod designer to prepare transformations
        codemod_designer = CodemodDesignerAgent(self.context)
        codemod_designer.run()
        
        # Run refactorer to apply transformations
        refactorer = RefactorerAgent(self.context)
        refactorer.run_auto()
        
        # Show git diff after migration (primary strategy)
        self._show_git_diff()
    
    def run_apply_review(self):
        """
        Run the apply phase in review mode (interactive confirmation).
        """
        from migratex.agents.refactorer import RefactorerAgent
        from migratex.agents.codemod_designer import CodemodDesignerAgent
        from migratex.utils.file_ops import copy_project_structure
        
        # Set up git branch if enabled (primary strategy)
        self._setup_git_branch()
        
        # If output_dir is set, copy project structure first
        if self.context.output_dir:
            copy_project_structure(self.context.project_path, self.context.output_dir)
            if self.context.verbose:
                print(f"Copied project structure to: {self.context.output_dir}")
        
        # Load relevant patterns
        self.context.load_patterns()
        
        # Run codemod designer to prepare transformations
        codemod_designer = CodemodDesignerAgent(self.context)
        codemod_designer.run()
        
        # Run refactorer in review mode
        refactorer = RefactorerAgent(self.context)
        refactorer.run_review()
        
        # Show git diff after migration (primary strategy)
        self._show_git_diff()

