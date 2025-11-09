#!/usr/bin/env python3
"""
Test Quality Monitor Script

Monitors test quality and blocks commits/releases if standards not met.
Implements TESTING_REDEMPTION_PLAN.md standards.

Usage:
    python scripts/test_quality_monitor.py [--directory DIRECTORY]
    
Checks:
- Weak assertions (>= 0, isinstance without value checks, etc.)
- Real-world test presence
- Outcome verification in assertions
- Strong assertion patterns

Exits with code 1 if issues found, 0 if all checks pass.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import argparse


@dataclass
class QualityIssue:
    """Represents a test quality issue."""
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str  # 'critical', 'warning', 'info'


class TestQualityMonitor:
    """Monitor test quality and detect weak assertions."""
    
    # Weak assertion patterns (FORBIDDEN)
    WEAK_PATTERNS = [
        # Length checks that are always true
        (r'assert\s+len\([^)]+\)\s*>=\s*0', 'Length >= 0 is always true'),
        (r'assert\s+len\([^)]+\)\s*>\s*-1', 'Length > -1 is always true'),
        
        # Instance checks without value verification
        (r'assert\s+isinstance\([^,]+,\s*dict\)\s*$', 'isinstance(dict) without value check'),
        (r'assert\s+isinstance\([^,]+,\s*list\)\s*$', 'isinstance(list) without value check'),
        (r'assert\s+isinstance\([^,]+,\s*str\)\s*$', 'isinstance(str) without value check'),
        (r'assert\s+isinstance\([^,]+,\s*int\)\s*$', 'isinstance(int) without value check'),
        
        # Existence checks without value verification
        (r'assert\s+\w+\s+is\s+not\s+None\s*$', 'Not None check without value verification'),
        (r'assert\s+\w+\s*$', 'Boolean assertion without specific check'),
        
        # Exit code checks without outcome verification
        (r'assert\s+\w+\.exit_code\s+in\s+\[0,\s*1\]', 'Exit code check without outcome verification'),
        (r'assert\s+\w+\.returncode\s+==\s*0\s*$', 'Return code 0 without outcome verification'),
        
        # Count checks that don't verify actual content
        (r'assert\s+len\([^)]+\)\s*>=\s*\d+\s*$', 'Length check without content verification'),
    ]
    
    # Required patterns for strong assertions
    STRONG_PATTERNS = [
        'assert.*>.*0.*,',  # With error message
        'assert.*in.*,',     # With error message
        'assert.*==.*,',     # With error message
        'verify_',           # Custom verification functions
        'check_',            # Custom check functions
    ]
    
    # Real-world test indicators
    REAL_WORLD_INDICATORS = [
        'clone_',
        'real_repo',
        'semantic-kernel',
        'autogen',
        'production',
        'actual_repo',
        '@pytest.mark.real_world',
        'test_real_world',
    ]
    
    def __init__(self, test_directory: Path):
        """Initialize the monitor with the test directory."""
        self.test_directory = Path(test_directory)
        self.issues: List[QualityIssue] = []
        self.stats = {
            'total_files': 0,
            'total_assertions': 0,
            'weak_assertions': 0,
            'missing_real_world': 0,
            'missing_outcome_verification': 0,
        }
    
    def scan_all_tests(self) -> bool:
        """Scan all test files for quality issues."""
        print(f"\n[SCAN] Scanning tests in {self.test_directory}...")
        
        test_files = list(self.test_directory.rglob('test_*.py'))
        self.stats['total_files'] = len(test_files)
        
        for test_file in test_files:
            self._scan_file(test_file)
        
        return len(self.issues) == 0
    
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single test file for quality issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Scan for weak assertions
            self._scan_weak_assertions(file_path, lines)
            
            # Check for real-world tests
            self._check_real_world_tests(file_path, content)
            
            # Check for outcome verification
            self._check_outcome_verification(file_path, content, lines)
            
        except Exception as e:
            self.issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=0,
                issue_type='scan_error',
                description=f'Error scanning file: {str(e)}',
                severity='warning'
            ))
    
    def _scan_weak_assertions(self, file_path: Path, lines: List[str]) -> None:
        """Scan for weak assertion patterns."""
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            # Check for weak patterns
            for pattern, description in self.WEAK_PATTERNS:
                if re.search(pattern, line_stripped):
                    self.issues.append(QualityIssue(
                        file_path=str(file_path.relative_to(self.test_directory.parent)),
                        line_number=line_num,
                        issue_type='weak_assertion',
                        description=description,
                        severity='critical'
                    ))
                    self.stats['weak_assertions'] += 1
            
            # Count total assertions
            if 'assert' in line_stripped and not line_stripped.startswith('#'):
                self.stats['total_assertions'] += 1
    
    def _check_real_world_tests(self, file_path: Path, content: str) -> None:
        """Check if file contains real-world tests."""
        # E2E and integration tests should have real-world tests
        if 'e2e' in str(file_path) or 'integration' in str(file_path):
            has_real_world = any(
                indicator in content.lower()
                for indicator in self.REAL_WORLD_INDICATORS
            )
            
            if not has_real_world:
                self.issues.append(QualityIssue(
                    file_path=str(file_path.relative_to(self.test_directory.parent)),
                    line_number=0,
                    issue_type='missing_real_world',
                    description='E2E/Integration test missing real-world validation',
                    severity='critical'
                ))
                self.stats['missing_real_world'] += 1
    
    def _check_outcome_verification(
        self, 
        file_path: Path, 
        content: str, 
        lines: List[str]
    ) -> None:
        """Check if tests verify actual outcomes."""
        # Look for test functions
        test_functions = [
            i for i, line in enumerate(lines)
            if line.strip().startswith('def test_')
        ]
        
        for func_start in test_functions:
            # Get function body (simplified - just next 50 lines)
            func_end = min(func_start + 50, len(lines))
            func_body = '\n'.join(lines[func_start:func_end])
            
            # Check if function verifies outcomes
            has_verification = (
                'verify' in func_body.lower() or
                'check' in func_body.lower() or
                'transformed' in func_body.lower() or
                'updated' in func_body.lower() or
                'written' in func_body.lower() or
                re.search(r'assert.*>\s*0', func_body) or
                re.search(r'assert.*in\s+', func_body)
            )
            
            # Only flag if test has assertions but no verification
            has_assertions = 'assert' in func_body
            
            if has_assertions and not has_verification:
                func_name = lines[func_start].strip()
                self.issues.append(QualityIssue(
                    file_path=str(file_path.relative_to(self.test_directory.parent)),
                    line_number=func_start + 1,
                    issue_type='missing_outcome_verification',
                    description=f'Test {func_name} may not verify actual outcomes',
                    severity='warning'
                ))
                self.stats['missing_outcome_verification'] += 1
    
    def generate_report(self) -> str:
        """Generate a quality report."""
        report = []
        report.append("\n" + "=" * 80)
        report.append("TEST QUALITY REPORT")
        report.append("=" * 80)
        
        # Statistics
        report.append(f"\n[STATISTICS]:")
        report.append(f"  Total test files: {self.stats['total_files']}")
        report.append(f"  Total assertions: {self.stats['total_assertions']}")
        report.append(f"  Weak assertions: {self.stats['weak_assertions']}")
        report.append(f"  Missing real-world tests: {self.stats['missing_real_world']}")
        report.append(f"  Missing outcome verification: {self.stats['missing_outcome_verification']}")
        
        # Issues by severity
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        warning_issues = [i for i in self.issues if i.severity == 'warning']
        
        report.append(f"\n[ISSUES FOUND]:")
        report.append(f"  Critical: {len(critical_issues)}")
        report.append(f"  Warnings: {len(warning_issues)}")
        
        # Critical issues
        if critical_issues:
            report.append(f"\n[CRITICAL ISSUES] (MUST FIX):")
            for issue in critical_issues[:20]:  # Show first 20
                report.append(
                    f"  {issue.file_path}:{issue.line_number} - "
                    f"{issue.issue_type}: {issue.description}"
                )
            
            if len(critical_issues) > 20:
                report.append(f"  ... and {len(critical_issues) - 20} more critical issues")
        
        # Warning issues (sample)
        if warning_issues:
            report.append(f"\n[WARNINGS] (SHOULD FIX):")
            for issue in warning_issues[:10]:  # Show first 10
                report.append(
                    f"  {issue.file_path}:{issue.line_number} - "
                    f"{issue.issue_type}: {issue.description}"
                )
            
            if len(warning_issues) > 10:
                report.append(f"  ... and {len(warning_issues) - 10} more warnings")
        
        # Verdict
        report.append(f"\n" + "=" * 80)
        if len(critical_issues) > 0:
            report.append("[FAIL] TEST QUALITY CHECK FAILED")
            report.append(f"   Fix {len(critical_issues)} critical issues before committing")
        elif len(warning_issues) > 0:
            report.append("[WARN] TEST QUALITY CHECK PASSED WITH WARNINGS")
            report.append(f"   Consider fixing {len(warning_issues)} warnings")
        else:
            report.append("[PASS] TEST QUALITY CHECK PASSED")
            report.append("   All tests meet quality standards")
        
        report.append("=" * 80 + "\n")
        
        return '\n'.join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Monitor test quality and detect weak assertions'
    )
    parser.add_argument(
        '--directory',
        default='tests',
        help='Directory containing tests (default: tests)'
    )
    
    args = parser.parse_args()
    
    # Initialize monitor
    test_dir = Path(args.directory)
    if not test_dir.exists():
        print(f"[ERROR] Test directory '{test_dir}' does not exist")
        return 1
    
    monitor = TestQualityMonitor(test_dir)
    
    # Scan tests
    success = monitor.scan_all_tests()
    
    # Generate report
    report = monitor.generate_report()
    print(report)
    
    # Exit with appropriate code
    critical_issues = [i for i in monitor.issues if i.severity == 'critical']
    if critical_issues:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

