"""
Analyze command - Read-only discovery phase
"""

import click
import json
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.cli.ui_helpers import CLIFormatter


@click.command("analyze")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path))
@click.option("--out", "-o", type=click.Path(path_type=Path), help="Output JSON report file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def analyze_command(path: Path, out: Path | None, verbose: bool):
    """
    Analyse codebase for Semantic Kernel/AutoGen patterns.
    
    This is a read-only discovery phase that scans the codebase and generates
    a report of detected patterns without making any code changes.
    """
    # Print header using Option 1 style
    CLIFormatter.header("MigrateX - Analysis")
    
    CLIFormatter.field("Project", str(path))
    CLIFormatter.field("Mode", "Analysis (read-only)")
    if out:
        CLIFormatter.field("Output", str(out))
    
    CLIFormatter.separator()
    
    # Create migration context
    context = MigrationContext(
        project_path=path,
        verbose=verbose
    )
    
    # Create orchestrator
    orchestrator = Orchestrator(context)
    
    # Run analysis phase
    try:
        CLIFormatter.progress("Scanning project files...")
        orchestrator.run_analysis()
        
        # Generate report
        report = context.get_report()
        
        CLIFormatter.separator()
        CLIFormatter.section("RESULTS")
        
        files_count = len(report.get('files', []))
        patterns_count = len(report.get('patterns', []))
        
        CLIFormatter.field("Files scanned", files_count)
        CLIFormatter.field("Patterns detected", patterns_count)
        
        # Output results
        if out:
            with open(out, "w") as f:
                json.dump(report, f, indent=2)
            CLIFormatter.separator()
            CLIFormatter.success(f"Analysis complete! Report saved to: {out}")
        else:
            if verbose:
                click.echo("\nDetailed Report:")
                click.echo(json.dumps(report, indent=2))
            else:
                CLIFormatter.separator()
                CLIFormatter.success("Analysis complete!")
        
        # Display outlier warnings using Option 1 style
        outlier_report = report.get('outlier_report', {})
        if outlier_report.get('is_outlier'):
            CLIFormatter.outlier_warning_box(outlier_report)
        
        
    except Exception as e:
        CLIFormatter.separator()
        CLIFormatter.error(f"Analysis failed: {str(e)}")
        if verbose:
            import traceback
            click.echo("\nStack trace:", err=True)
            traceback.print_exc()
        raise click.Abort()

