#!/usr/bin/env python3
"""
MigrateX - CLI entry point
Semi-automated migration assistant for migrating Semantic Kernel and AutoGen code to Microsoft Agent Framework
"""

import sys
from migratex.cli.main import cli

if __name__ == "__main__":
    sys.exit(cli())

