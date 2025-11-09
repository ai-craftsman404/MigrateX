"""
Batch fix script for test fixtures and missing analysis steps.

This script systematically fixes:
1. All git repo fixtures to use safe_rmtree
2. All tests missing analysis step before run_apply_auto
"""

import re
from pathlib import Path


def fix_git_fixtures():
    """Fix all git repo fixtures to use safe_rmtree."""
    files_to_fix = [
        "tests/integration/test_git_workflow.py",
        "tests/integration/test_git_branch_workflow.py",
        "tests/performance/test_git_performance.py",
        "tests/edge_cases/test_git_edge_cases.py",
        "tests/unit/test_git_ops.py",
        "tests/windows/test_console_encoding.py",
    ]
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            continue
        
        content = path.read_text()
        
        # Replace shutil.rmtree(temp_dir) with safe_rmtree
        if "shutil.rmtree(temp_dir)" in content or "shutil.rmtree(repo)" in content:
            # Add import if not present
            if "from tests.utils.cleanup import safe_rmtree" not in content:
                # Find import section
                import_match = re.search(r'(import shutil)', content)
                if import_match:
                    content = content[:import_match.end()] + "\nfrom tests.utils.cleanup import safe_rmtree" + content[import_match.end():]
                elif "import shutil" in content:
                    # Add after existing imports
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "import shutil" in line:
                            lines.insert(i + 1, "from tests.utils.cleanup import safe_rmtree")
                            break
                    content = '\n'.join(lines)
            
            # Replace shutil.rmtree calls
            content = re.sub(
                r'shutil\.rmtree\((temp_dir|repo|fixture|git_repo[_\w]*)\)',
                r'safe_rmtree(\1)',
                content
            )
            
            path.write_text(content)
            print(f"Fixed: {file_path}")


def fix_missing_analysis():
    """Fix all tests missing analysis step before run_apply_auto."""
    files_to_fix = [
        "tests/integration/test_git_workflow.py",
    ]
    
    for file_path in files_to_fix:
        path = Path(file_path)
        if not path.exists():
            continue
        
        content = path.read_text()
        
        # Find patterns like:
        # orchestrator = Orchestrator(context)
        # orchestrator.run_apply_auto()
        # Should become:
        # orchestrator = Orchestrator(context)
        # orchestrator.run_analysis()
        # orchestrator.run_apply_auto()
        
        pattern = r'(orchestrator\s*=\s*Orchestrator\([^)]+\))\s*\n\s*(orchestrator\.run_apply_auto\(\))'
        replacement = r'\1\n        orchestrator.run_analysis()\n        \2'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            path.write_text(content)
            print(f"Fixed missing analysis in: {file_path}")


if __name__ == "__main__":
    print("Fixing git fixtures...")
    fix_git_fixtures()
    
    print("\nFixing missing analysis steps...")
    fix_missing_analysis()
    
    print("\nDone!")

