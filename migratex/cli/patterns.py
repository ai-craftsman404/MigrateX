"""
Patterns command group - Pattern management
"""

import click
from pathlib import Path
from migratex.patterns.cache import PatternCache
from migratex.patterns.library import PatternLibrary


@click.group("patterns")
def patterns_group():
    """
    Manage transformation patterns and pattern cache.
    """
    pass


@patterns_group.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed pattern information")
def list_patterns(verbose: bool):
    """
    List all known transformation patterns.
    """
    library = PatternLibrary()
    patterns = library.get_all_patterns()
    
    click.echo(f"Found {len(patterns)} patterns:\n")
    
    for pattern_id, pattern in patterns.items():
        click.echo(f"  {pattern_id}")
        if verbose:
            click.echo(f"    Confidence: {pattern.get('confidence', 'unknown')}")
            click.echo(f"    Source: {pattern.get('source', 'unknown')}")
            click.echo(f"    Description: {pattern.get('description', 'No description')}")
            click.echo()


@patterns_group.command("cache")
@click.option("--clear", is_flag=True, help="Clear the pattern cache")
@click.option("--path", type=click.Path(path_type=Path), help="Pattern cache file path")
def cache_command(clear: bool, path: Path | None):
    """
    Manage pattern cache.
    """
    cache_path = path or Path.cwd() / "pattern-cache.yaml"
    
    if clear:
        cache = PatternCache(cache_path)
        cache.clear()
        click.echo(f"Pattern cache cleared: {cache_path}")
    else:
        cache = PatternCache(cache_path)
        if cache.exists():
            patterns = cache.get_all_decisions()
            click.echo(f"Pattern cache at: {cache_path}")
            click.echo(f"Cached decisions: {len(patterns)}")
            for pattern_id, decision in patterns.items():
                click.echo(f"  {pattern_id}: {decision.get('decision', 'unknown')}")
        else:
            click.echo(f"No pattern cache found at: {cache_path}")

