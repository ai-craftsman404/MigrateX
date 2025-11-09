"""
Unit tests for Outlier Detection (Agent 5)

Tests outlier detection system and handling.
Target: 10+ tests for outlier detection
"""

import pytest
from pathlib import Path
from migratex.testing.outlier_detector import OutlierDetector
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures, OutlierTestFixtures


class TestOutlierDetection:
    """Test outlier detection system."""
    
    def test_monorepo_detection(self):
        """Test detection of monorepo structure."""
        fixture = OutlierTestFixtures.create_monorepo_structure()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "monorepo" in report["outlier_types"]
            assert report["risk_level"] in ["low", "medium", "high", "critical"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_namespace_package_detection(self):
        """Test detection of namespace packages."""
        fixture = OutlierTestFixtures.create_namespace_package_codebase()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "namespace_packages" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_generated_code_detection(self):
        """Test detection of generated code directories."""
        fixture = OutlierTestFixtures.create_generated_code_codebase()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "generated_code" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_large_file_detection(self):
        """Test detection of very large files."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=15000)
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "large_files" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_deep_nesting_detection(self):
        """Test detection of deeply nested structures."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=25)
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "deep_nesting" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_normal_codebase_not_outlier(self):
        """Test that normal codebase is not flagged as outlier."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel\n\nclass MyAgent:\n    pass"
        )
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # Normal small codebase should not be outlier
            assert report["is_outlier"] == False or report["risk_level"] == "low"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_outlier_report_structure(self):
        """Test that outlier report has correct structure."""
        fixture = OutlierTestFixtures.create_monorepo_structure()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert "is_outlier" in report
            assert "outlier_types" in report
            assert "confidence" in report
            assert "risk_level" in report
            assert "risks" in report
            assert "recommendations" in report
            assert "details" in report
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_risk_level_calculation(self):
        """Test that risk levels are calculated correctly."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=20000)
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["risk_level"] in ["low", "medium", "high", "critical"]
            # Large files should be at least medium risk
            if "large_files" in report["outlier_types"]:
                assert report["risk_level"] in ["medium", "high", "critical"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_confidence_calculation(self):
        """Test that confidence scores are calculated."""
        fixture = OutlierTestFixtures.create_monorepo_structure()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert 0.0 <= report["confidence"] <= 1.0
            if report["is_outlier"]:
                assert report["confidence"] > 0.0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_recommendations_provided(self):
        """Test that recommendations are provided for outliers."""
        fixture = OutlierTestFixtures.create_monorepo_structure()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            if report["is_outlier"]:
                assert len(report["recommendations"]) > 0
                assert all(isinstance(rec, str) for rec in report["recommendations"])
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

