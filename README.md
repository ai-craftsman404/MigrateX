# MigrateX - Migration Tool for SK/AutoGen to MAF

A semi-automated migration assistant that scans, analyses, and refactors code from Semantic Kernel and AutoGen frameworks to Microsoft Agent Framework.

## Installation

```bash
pip install -e .
```

## Usage

### Analyse codebase (read-only discovery)

```bash
migrate analyze /path/to/project --out report.json --verbose
```

### Apply migrations automatically (high-confidence)

```bash
migrate apply /path/to/project --auto --pattern-cache cache.yaml --summary summary.md
```

**Git Integration (Default - Primary Strategy):**
By default, MigrateX creates a git branch (`migratex/migrate-to-maf`) and shows git diff after migration:

```bash
# Uses git branch by default
migrate apply /path/to/project --auto

# Custom branch name
migrate apply /path/to/project --auto --branch-name "my-migration-branch"

# Disable git operations
migrate apply /path/to/project --auto --no-git-branch

# Disable git diff display
migrate apply /path/to/project --auto --no-show-diff
```

### Apply migrations with review (interactive)

```bash
migrate apply /path/to/project --review --diff --remember-decisions
```

### Manage patterns

```bash
migrate patterns list
migrate patterns cache --clear
```

## Architecture

- **CLI-first**: Python CLI tool as primary interface
- **Agent-based**: Specialized agents for different concerns
- **Pattern-driven**: Rule-based pattern detection and transformation
- **Python MVP**: Initial support for Python codebases

## Project Structure

- **`migratex/`**: Core CLI tool (MVP)
- **`extension/`**: VS Code extension (Phase 2+)
- **`tests/`**: Test suite
- **`migratex/docs/`**: Documentation and migration guides

## Development

This tool is under active development.

**Note**: VS Code extension is planned for Phase 2. Current MVP focuses on CLI functionality.
