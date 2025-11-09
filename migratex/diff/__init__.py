"""
Diff generation module
"""

from typing import Tuple
from diff_match_patch import diff_match_patch


class DiffGenerator:
    """
    Generates diffs for before/after code comparison.
    """
    
    def __init__(self):
        self.dmp = diff_match_patch()
    
    def generate_diff(self, before: str, after: str) -> str:
        """
        Generate unified diff between before and after code.
        """
        diffs = self.dmp.diff_main(before, after)
        self.dmp.diff_cleanupSemantic(diffs)
        
        # Convert to unified diff format
        diff_text = self.dmp.diff_prettyHtml(diffs)
        return diff_text
    
    def generate_unified_diff(self, file_path: str, before: str, after: str) -> str:
        """
        Generate unified diff format (like git diff).
        """
        lines_before = before.splitlines(keepends=True)
        lines_after = after.splitlines(keepends=True)
        
        diff_lines = [f"--- {file_path}", f"+++ {file_path}"]
        
        # Simple line-by-line diff (can be enhanced)
        for i, (line_before, line_after) in enumerate(zip(lines_before, lines_after)):
            if line_before != line_after:
                diff_lines.append(f"@@ -{i+1},1 +{i+1},1 @@")
                diff_lines.append(f"-{line_before}")
                diff_lines.append(f"+{line_after}")
        
        return "".join(diff_lines)

