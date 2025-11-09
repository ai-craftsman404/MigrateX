"""
Apply command - Code transformation phase
"""

import click
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.cli.ui_helpers import CLIFormatter


@click.command("apply")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--auto", is_flag=True, help="Apply high-confidence transformations automatically")
@click.option("--review", is_flag=True, help="Interactive confirmation mode")
@click.option("--report", type=click.Path(path_type=Path), help="Input report file from analyze phase")
@click.option("--pattern-cache", type=click.Path(path_type=Path), help="Pattern cache file")
@click.option("--summary", type=click.Path(path_type=Path), help="Output summary markdown file")
@click.option("--remember-decisions", is_flag=True, help="Remember user decisions in pattern cache")
@click.option("--diff", is_flag=True, help="Show diffs before applying changes")
@click.option("--review-mode", type=click.Choice(["pattern", "file", "none"]), default="pattern", 
              help="Review granularity: pattern (default), file, or none")
@click.option("--on-error", type=click.Choice(["continue", "stop"]), default="continue",
              help="Error handling: continue (default) or stop on first failure")
@click.option("--output-dir", type=click.Path(path_type=Path), help="Output directory for migrated code (preserves original)")
@click.option("--git-branch/--no-git-branch", default=True, 
              help="Create git branch for migration (default: enabled - primary strategy)")
@click.option("--branch-name", type=str, default="migratex/migrate-to-maf",
              help="Git branch name (default: migratex/migrate-to-maf)")
@click.option("--show-diff/--no-show-diff", default=True,
              help="Show git diff after migration (default: enabled)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def apply_command(
    path: Path,
    auto: bool,
    review: bool,
    report: Path | None,
    pattern_cache: Path | None,
    summary: Path | None,
    remember_decisions: bool,
    diff: bool,
    review_mode: str,
    on_error: str,
    output_dir: Path | None,
    git_branch: bool,
    branch_name: str,
    show_diff: bool,
    verbose: bool
):
    """
    Apply migrations to transform code from SK/AutoGen to MAF.
    
    Requires analysis report from 'migrate analyze' command.
    Use --auto for high-confidence transformations or --review for interactive mode.
    Use --output-dir to store migrated code separately (original code preserved).
    
    Git Integration (Primary Strategy):
    By default, creates a git branch (migratex/migrate-to-maf) and shows git diff after migration.
    Use --no-git-branch to disable git operations.
    
    Example:
        migrate analyze . --out report.json
        migrate apply . --auto --report report.json
    """
    if not auto and not review:
        CLIFormatter.error("Must specify either --auto or --review")
        raise click.Abort()
    
    if auto and review:
        CLIFormatter.error("Cannot use both --auto and --review")
        raise click.Abort()
    
    mode = "auto" if auto else "review"
    
    # Print header using Option 1 style
    CLIFormatter.header("MigrateX - Apply Migration")
    
    CLIFormatter.field("Project", str(path))
    mode_desc = "Auto (high-confidence)" if auto else "Review (interactive)"
    CLIFormatter.field("Mode", mode_desc)
    if output_dir:
        CLIFormatter.field("Output directory", f"{output_dir} (original preserved)")
    if git_branch:
        CLIFormatter.field("Git branch", f"{branch_name} (will be created)")
    
    CLIFormatter.separator()
    
    # Load report if provided
    report_data = None
    if report and report.exists():
        import json
        CLIFormatter.progress("Loading analysis report...")
        with open(report, "r") as f:
            report_data = json.load(f)
    
    # Create migration context
    context = MigrationContext(
        project_path=path,
        mode=mode,
        pattern_cache_path=pattern_cache,
        remember_decisions=remember_decisions,
        show_diff=diff,
        review_granularity=review_mode,
        error_policy=on_error,
        output_dir=output_dir,
        use_git_branch=git_branch,
        git_branch_name=branch_name,
        show_git_diff=show_diff,
        verbose=verbose,
        interactive=False
    )
    
    # Load report data into context if provided
    if report_data:
        context.report = report_data
    else:
        # Require report file - no auto-run
        CLIFormatter.separator()
        CLIFormatter.error("No analysis report provided. Run 'migrate analyze' first.")
        CLIFormatter.info("Usage: migrate apply <path> --auto --report <report-file>")
        raise click.Abort()
    
    # Create orchestrator
    orchestrator = Orchestrator(context)
    
    # Run apply phase
    try:
        CLIFormatter.separator()
        CLIFormatter.progress("Starting migration...")
        
        if mode == "auto":
            orchestrator.run_apply_auto()
        else:
            orchestrator.run_apply_review()
        
        CLIFormatter.separator()
        CLIFormatter.section("RESULTS")
        
        # Generate checkpoint
        checkpoint = context.get_checkpoint()
        updated_count = len(checkpoint.get('updated_files', []))
        failed_count = len(checkpoint.get('failed_files', []))
        
        CLIFormatter.field("Files transformed", updated_count)
        if failed_count > 0:
            CLIFormatter.field("Files failed", failed_count, "red")
        
        # Generate summary if requested
        if summary:
            context.write_summary(summary)
            CLIFormatter.separator()
            CLIFormatter.info(f"Summary saved to: {summary}")
        
        CLIFormatter.separator()
        CLIFormatter.success("Migration complete!")
        
    except Exception as e:
        CLIFormatter.separator()
        CLIFormatter.error(f"Migration failed: {str(e)}")
        if verbose:
            import traceback
            click.echo("\nStack trace:", err=True)
            traceback.print_exc()
        raise click.Abort()

