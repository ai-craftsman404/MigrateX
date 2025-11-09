"""
CLI main entry point for MigrateX
"""

import click
from migratex.cli.analyze import analyze_command
from migratex.cli.apply import apply_command
from migratex.cli.patterns import patterns_group
from migratex.cli.test import test_command
from migratex.cli.test_parallel import test_parallel_command


@click.group()
@click.version_option(version="0.0.1", prog_name="migrate")
def cli():
    """
    MigrateX - Migration tool for Semantic Kernel/AutoGen to Microsoft Agent Framework
    
    A semi-automated migration assistant that scans, analyses, and refactors code
    from Semantic Kernel and AutoGen frameworks to Microsoft Agent Framework.
    """
    pass


# Register subcommands
cli.add_command(analyze_command)
cli.add_command(apply_command)
cli.add_command(patterns_group)
cli.add_command(test_command)
cli.add_command(test_parallel_command)

