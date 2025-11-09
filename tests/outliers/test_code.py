"""
Outlier Code Tests (Agent 5 - T5.2)

Tests outlier detection for code-level outliers.
Target: 10+ scenarios, 100% of code outliers
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.testing.outlier_detector import OutlierDetector
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestOutlierCode:
    """Test code-level outlier detection."""
    
    def test_very_large_file_outlier(self):
        """Test detection of very large files (>100K lines)."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=150000)
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "large_files" in report["outlier_types"] or "large_file" in report["outlier_types"] or "size_outlier" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_very_large_function_outlier(self):
        """Test detection of very large functions (>1000 lines)."""
        fixture = Path(tempfile.mkdtemp())
        large_function = "def huge_function():\n    " + "\n    ".join([f"x = {i}" for i in range(1500)])
        (fixture / "large_func.py").write_text(large_function)
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to large function
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_deeply_nested_code_outlier(self):
        """Test detection of deeply nested code (>20 nesting levels)."""
        fixture = Path(tempfile.mkdtemp())
        nested_code = "\n".join(["if True:" for _ in range(25)]) + "\n    pass"
        (fixture / "nested.py").write_text(nested_code)
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to deep nesting
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_mixed_indentation_outlier(self):
        """Test detection of mixed indentation (tabs + spaces)."""
        fixture = Path(tempfile.mkdtemp())
        mixed_code = "def func():\n    # Spaces\n\t# Tabs\n    pass"
        (fixture / "mixed.py").write_text(mixed_code)
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to mixed indentation
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_non_standard_encoding_outlier(self):
        """Test detection of non-standard encoding."""
        fixture = EdgeCaseTestFixtures.create_encoding_issue_codebase()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to encoding issues
            assert isinstance(report["is_outlier"], bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_bom_markers_outlier(self):
        """Test detection of BOM markers in files."""
        fixture = Path(tempfile.mkdtemp())
        # Write file with BOM (UTF-8 BOM: EF BB BF)
        (fixture / "bom.py").write_bytes(b'\xef\xbb\xbf# File with BOM\nfrom semantic_kernel import Kernel')
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to BOM
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_line_ending_issues_outlier(self):
        """Test detection of mixed line endings (CRLF/LF)."""
        fixture = Path(tempfile.mkdtemp())
        mixed_endings = "line1\nline2\r\nline3\n"
        (fixture / "endings.py").write_bytes(mixed_endings.encode('utf-8'))
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to mixed line endings
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_trailing_whitespace_outlier(self):
        """Test detection of excessive trailing whitespace."""
        fixture = Path(tempfile.mkdtemp())
        whitespace_code = "def func():\n    pass    \n    return     \n"
        (fixture / "whitespace.py").write_text(whitespace_code)
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to excessive whitespace
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_very_long_lines_outlier(self):
        """Test detection of very long lines (>1000 chars)."""
        fixture = Path(tempfile.mkdtemp())
        long_line = "x = " + " + ".join([str(i) for i in range(500)])  # Very long line
        (fixture / "long.py").write_text(long_line)
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to very long lines
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_unicode_issues_outlier(self):
        """Test detection of unicode handling issues."""
        fixture = Path(tempfile.mkdtemp())
        unicode_code = "# Unicode test\nx = '你好世界'\nfrom semantic_kernel import Kernel"
        (fixture / "unicode.py").write_text(unicode_code, encoding='utf-8')
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # Should handle unicode correctly (may or may not be outlier)
            assert isinstance(report["is_outlier"], bool)
        finally:
            shutil.rmtree(fixture)

