#!/usr/bin/env python3
"""
Test Audit Script

Comprehensive test audit that scans, categorizes, and provides fix suggestions.
Implements code-analyzer agent behaviour for test quality analysis.

Usage:
    python scripts/audit_tests.py [--directory DIRECTORY] [--output OUTPUT]
    
Features:
- Comprehensive test scanning
- Issue categorization
- Fix suggestions
- Detailed reporting
- Export to JSON/Markdown

Exits with code 1 if issues found, 0 if all checks pass.
"""

import ast
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Set, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse


@dataclass
class TestIssue:
    """Represents a test issue with fix suggestions."""
    file_path: str
    line_number: int
    issue_category: str
    issue_type: str
    severity: str
    description: str
    current_code: str
    suggested_fix: str
    rationale: str


class TestAuditor:
    """Comprehensive test auditor with fix suggestions."""
    
    ISSUE_CATEGORIES = {
        'weak_assertions': 'Weak Assertions',
        'missing_real_world': 'Missing Real-World Tests',
        'missing_outcome_verification': 'Missing Outcome Verification',
        'poor_test_structure': 'Poor Test Structure',
        'missing_error_messages': 'Missing Assertion Error Messages',
        'synthetic_only': 'Synthetic-Only Tests',
    }
    
    def __init__(self, test_directory: Path):
        """Initialize the auditor."""
        self.test_directory = Path(test_directory)
        self.issues: List[TestIssue] = []
        self.stats = {
            'total_files': 0,
            'total_tests': 0,
            'total_assertions': 0,
            'issues_by_category': {cat: 0 for cat in self.ISSUE_CATEGORIES},
        }
    
    def audit_all_tests(self) -> bool:
        """Perform comprehensive audit of all tests."""
        print(f"\n[AUDIT] Auditing tests in {self.test_directory}...")
        
        test_files = list(self.test_directory.rglob('test_*.py'))
        self.stats['total_files'] = len(test_files)
        
        for test_file in test_files:
            self._audit_file(test_file)
        
        return len(self.issues) == 0
    
    def _audit_file(self, file_path: Path) -> None:
        """Audit a single test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for better analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree, lines)
            except SyntaxError:
                pass  # Skip files with syntax errors
            
            # Scan for weak assertions
            self._audit_weak_assertions(file_path, lines)
            
            # Check for missing error messages
            self._audit_error_messages(file_path, lines)
            
            # Check for real-world tests
            self._audit_real_world_tests(file_path, content, lines)
            
            # Check for outcome verification
            self._audit_outcome_verification(file_path, lines)
            
        except Exception as e:
            print(f"Warning: Error auditing {file_path}: {e}")
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST, lines: List[str]) -> None:
        """Analyze AST for test structure issues."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    self.stats['total_tests'] += 1
                    
                    # Check for empty test functions
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        self.issues.append(TestIssue(
                            file_path=str(file_path.relative_to(self.test_directory.parent)),
                            line_number=node.lineno,
                            issue_category='poor_test_structure',
                            issue_type='empty_test',
                            severity='critical',
                            description='Empty test function',
                            current_code=f'def {node.name}():\n    pass',
                            suggested_fix='Remove or implement test',
                            rationale='Empty tests provide no value and mislead test coverage'
                        ))
                        self.stats['issues_by_category']['poor_test_structure'] += 1
            
            elif isinstance(node, ast.Assert):
                self.stats['total_assertions'] += 1
    
    def _audit_weak_assertions(self, file_path: Path, lines: List[str]) -> None:
        """Audit for weak assertion patterns."""
        weak_patterns = [
            # Pattern, suggested fix, rationale
            (
                r'assert\s+len\(([^)]+)\)\s*>=\s*0',
                lambda m: f'assert len({m.group(1)}) > 0, "Expected items in {m.group(1)}"',
                'Length >= 0 is always true; use > 0 to verify actual content'
            ),
            (
                r'assert\s+isinstance\(([^,]+),\s*dict\)\s*$',
                lambda m: f'assert isinstance({m.group(1)}, dict) and len({m.group(1)}) > 0, "Expected non-empty dict"',
                'isinstance checks only type, not value; add content verification'
            ),
            (
                r'assert\s+isinstance\(([^,]+),\s*list\)\s*$',
                lambda m: f'assert isinstance({m.group(1)}, list) and len({m.group(1)}) > 0, "Expected non-empty list"',
                'isinstance checks only type, not value; add content verification'
            ),
            (
                r'assert\s+(\w+)\s+is\s+not\s+None\s*$',
                lambda m: f'assert {m.group(1)} is not None and {m.group(1)} != "", "Expected valid {m.group(1)}"',
                'Not None check without value verification; add value check'
            ),
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            for pattern, fix_func, rationale in weak_patterns:
                match = re.search(pattern, line_stripped)
                if match:
                    self.issues.append(TestIssue(
                        file_path=str(file_path.relative_to(self.test_directory.parent)),
                        line_number=line_num,
                        issue_category='weak_assertions',
                        issue_type='weak_assertion_pattern',
                        severity='critical',
                        description='Weak assertion that may not verify actual functionality',
                        current_code=line_stripped,
                        suggested_fix=fix_func(match),
                        rationale=rationale
                    ))
                    self.stats['issues_by_category']['weak_assertions'] += 1
    
    def _audit_error_messages(self, file_path: Path, lines: List[str]) -> None:
        """Audit for assertions missing error messages."""
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for assert without error message
            if line_stripped.startswith('assert ') and ',' not in line_stripped:
                # Ignore simple boolean assertions
                if not re.search(r'assert\s+\w+\s*$', line_stripped):
                    self.issues.append(TestIssue(
                        file_path=str(file_path.relative_to(self.test_directory.parent)),
                        line_number=line_num,
                        issue_category='missing_error_messages',
                        issue_type='missing_error_message',
                        severity='warning',
                        description='Assertion missing error message',
                        current_code=line_stripped,
                        suggested_fix=f'{line_stripped}, "Add descriptive error message"',
                        rationale='Error messages help diagnose test failures quickly'
                    ))
                    self.stats['issues_by_category']['missing_error_messages'] += 1
    
    def _audit_real_world_tests(
        self, 
        file_path: Path, 
        content: str, 
        lines: List[str]
    ) -> None:
        """Audit for real-world test presence."""
        # Check if E2E or integration test
        is_e2e = 'e2e' in str(file_path)
        is_integration = 'integration' in str(file_path)
        
        if not (is_e2e or is_integration):
            return
        
        # Look for real-world indicators
        real_world_indicators = [
            'clone_', 'real_repo', 'semantic-kernel', 'autogen',
            'production', 'actual_repo', '@pytest.mark.real_world',
            'test_real_world',
        ]
        
        has_real_world = any(
            indicator in content.lower()
            for indicator in real_world_indicators
        )
        
        if not has_real_world:
            self.issues.append(TestIssue(
                file_path=str(file_path.relative_to(self.test_directory.parent)),
                line_number=0,
                issue_category='missing_real_world',
                issue_type='no_real_world_tests',
                severity='critical',
                description=f'{"E2E" if is_e2e else "Integration"} test file missing real-world tests',
                current_code='N/A',
                suggested_fix='Add @pytest.mark.real_world test using actual repository',
                rationale='Real-world tests are mandatory for E2E and integration testing'
            ))
            self.stats['issues_by_category']['missing_real_world'] += 1
    
    def _audit_outcome_verification(self, file_path: Path, lines: List[str]) -> None:
        """Audit for outcome verification in tests."""
        # Find test functions
        test_functions = []
        for i, line in enumerate(lines):
            if line.strip().startswith('def test_'):
                # Extract function body
                indent = len(line) - len(line.lstrip())
                func_lines = [line]
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                        break
                    func_lines.append(lines[j])
                test_functions.append((i + 1, func_lines))
        
        # Check each test function
        for line_num, func_lines in test_functions:
            func_body = '\n'.join(func_lines)
            
            # Check if function verifies outcomes
            outcome_indicators = [
                'transformed', 'updated', 'written', 'created',
                'modified', 'generated', 'files_transformed',
                'maf_code', 'verify_', 'check_'
            ]
            
            has_outcome_verification = any(
                indicator in func_body.lower()
                for indicator in outcome_indicators
            )
            
            # Has assertions but no outcome verification
            has_assertions = 'assert' in func_body
            
            if has_assertions and not has_outcome_verification:
                func_name = func_lines[0].strip()
                self.issues.append(TestIssue(
                    file_path=str(file_path.relative_to(self.test_directory.parent)),
                    line_number=line_num,
                    issue_category='missing_outcome_verification',
                    issue_type='no_outcome_verification',
                    severity='warning',
                    description='Test may not verify actual outcomes',
                    current_code=func_name,
                    suggested_fix='Add assertions that verify actual transformation outcomes',
                    rationale='Tests must verify functionality works, not just that code runs'
                ))
                self.stats['issues_by_category']['missing_outcome_verification'] += 1
    
    def generate_report(self, output_format: str = 'markdown') -> str:
        """Generate audit report in specified format."""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_markdown_report()
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown audit report."""
        lines = []
        lines.append("# Test Audit Report")
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        lines.append(f"- **Total Files Audited:** {self.stats['total_files']}")
        lines.append(f"- **Total Tests:** {self.stats['total_tests']}")
        lines.append(f"- **Total Assertions:** {self.stats['total_assertions']}")
        lines.append(f"- **Total Issues Found:** {len(self.issues)}\n")
        
        # Issues by Category
        lines.append("## Issues by Category\n")
        for category, count in self.stats['issues_by_category'].items():
            if count > 0:
                category_name = self.ISSUE_CATEGORIES[category]
                lines.append(f"- **{category_name}:** {count}")
        lines.append("")
        
        # Detailed Issues by Category
        for category, category_name in self.ISSUE_CATEGORIES.items():
            category_issues = [
                i for i in self.issues 
                if i.issue_category == category
            ]
            
            if not category_issues:
                continue
            
            lines.append(f"## {category_name}\n")
            
            # Group by severity
            critical = [i for i in category_issues if i.severity == 'critical']
            warnings = [i for i in category_issues if i.severity == 'warning']
            
            if critical:
                lines.append(f"### Critical Issues ({len(critical)})\n")
                for issue in critical[:10]:  # Show first 10
                    lines.append(f"#### {issue.file_path}:{issue.line_number}\n")
                    lines.append(f"**Description:** {issue.description}\n")
                    lines.append(f"**Current Code:**")
                    lines.append(f"```python")
                    lines.append(issue.current_code)
                    lines.append(f"```\n")
                    lines.append(f"**Suggested Fix:**")
                    lines.append(f"```python")
                    lines.append(issue.suggested_fix)
                    lines.append(f"```\n")
                    lines.append(f"**Rationale:** {issue.rationale}\n")
                
                if len(critical) > 10:
                    lines.append(f"*... and {len(critical) - 10} more critical issues*\n")
            
            if warnings:
                lines.append(f"### Warnings ({len(warnings)})\n")
                for issue in warnings[:5]:  # Show first 5
                    lines.append(f"- `{issue.file_path}:{issue.line_number}` - {issue.description}")
                
                if len(warnings) > 5:
                    lines.append(f"\n*... and {len(warnings) - 5} more warnings*\n")
        
        # Recommendations
        lines.append("\n## Recommendations\n")
        critical_count = sum(
            1 for i in self.issues if i.severity == 'critical'
        )
        
        if critical_count > 0:
            lines.append(f"1. **Fix {critical_count} critical issues immediately**")
            lines.append("2. Run this audit again to verify fixes")
            lines.append("3. Consider adding pre-commit hook to prevent future issues")
        else:
            lines.append("[PASS] No critical issues found!")
            warning_count = sum(
                1 for i in self.issues if i.severity == 'warning'
            )
            if warning_count > 0:
                lines.append(f"\nConsider addressing {warning_count} warnings for improved test quality.")
        
        return '\n'.join(lines)
    
    def _generate_json_report(self) -> str:
        """Generate JSON audit report."""
        report = {
            'generated': datetime.now().isoformat(),
            'statistics': self.stats,
            'issues': [asdict(issue) for issue in self.issues],
        }
        return json.dumps(report, indent=2)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Comprehensive test audit with fix suggestions'
    )
    parser.add_argument(
        '--directory',
        default='tests',
        help='Directory containing tests (default: tests)'
    )
    parser.add_argument(
        '--output',
        help='Output file path (optional)'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    args = parser.parse_args()
    
    # Initialize auditor
    test_dir = Path(args.directory)
    if not test_dir.exists():
        print(f"[ERROR] Test directory '{test_dir}' does not exist")
        return 1
    
    auditor = TestAuditor(test_dir)
    
    # Run audit
    success = auditor.audit_all_tests()
    
    # Generate report
    report = auditor.generate_report(args.format)
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[PASS] Report saved to {args.output}")
    else:
        print(report)
    
    # Exit with appropriate code
    critical_issues = [i for i in auditor.issues if i.severity == 'critical']
    if critical_issues:
        print(f"\n[FAIL] Audit failed: {len(critical_issues)} critical issues found")
        return 1
    
    print(f"\n[PASS] Audit passed!")
    return 0


if __name__ == '__main__':
    sys.exit(main())

