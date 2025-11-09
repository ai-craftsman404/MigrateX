"""
Documentation access utilities for agents.
"""

from migratex.docs import migration_docs


def get_migration_guide(framework: str):
    """Get migration guide for a framework."""
    return migration_docs.get_migration_guide(framework)


def get_pattern_mappings(framework: str):
    """Get pattern mappings for a framework."""
    return migration_docs.get_pattern_mappings(framework)


def get_best_practices():
    """Get migration best practices."""
    return migration_docs.get_best_practices()


def get_reference_urls():
    """Get reference documentation URLs."""
    return migration_docs.get_reference_urls()

