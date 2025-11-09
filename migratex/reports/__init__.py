"""
Reports module - Report generation
"""

from pathlib import Path
from typing import Dict, Any
import json


class ReportGenerator:
    """
    Generates reports in various formats (JSON, Markdown).
    """
    
    @staticmethod
    def generate_json_report(data: Dict[str, Any], output_path: Path):
        """Generate JSON report."""
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def generate_markdown_summary(data: Dict[str, Any], output_path: Path):
        """Generate Markdown summary."""
        lines = [
            "# Migration Report",
            "",
            f"## Statistics",
            f"- Total files: {data.get('statistics', {}).get('total_files', 0)}",
            f"- Patterns detected: {data.get('statistics', {}).get('patterns_detected', 0)}",
            "",
            "## Detected Patterns",
        ]
        
        for pattern in data.get("patterns", []):
            lines.append(f"- **{pattern.get('id', 'unknown')}**: {pattern.get('type', 'unknown')}")
            if "file" in pattern:
                lines.append(f"  - File: `{pattern['file']}`")
        
        with open(output_path, "w") as f:
            f.write("\n".join(lines))

