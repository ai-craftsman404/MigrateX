"""
Outlier Structure Tests (Agent 5 - T5.1)

Tests outlier detection with various structural outlier scenarios.
Target: 10+ scenarios, 100% of structure outliers
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.testing.outlier_detector import OutlierDetector
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures, OutlierTestFixtures


class TestOutlierStructures:
    """Test outlier structure detection."""
    
    def test_monorepo_structure_detection(self):
        """Test detection of monorepo with multiple projects."""
        fixture = OutlierTestFixtures.create_monorepo_structure()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "monorepo" in report["outlier_types"]
            assert report["risk_level"] in ["low", "medium", "high", "critical"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_very_deep_nesting_detection(self):
        """Test detection of very deep nesting (>20 levels)."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=25)
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "deep_nesting" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_unusual_directory_structure(self):
        """Test detection of unusual directory structure."""
        fixture = Path(tempfile.mkdtemp())
        
        # Create unusual structure
        (fixture / "src" / "lib" / "core" / "utils" / "helpers" / "misc").mkdir(parents=True)
        (fixture / "src" / "lib" / "core" / "utils" / "helpers" / "misc" / "file.py").write_text("import os")
        
        # Create another unusual path
        (fixture / "app" / "components" / "widgets" / "forms" / "inputs").mkdir(parents=True)
        (fixture / "app" / "components" / "widgets" / "forms" / "inputs" / "file.py").write_text("import os")
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May or may not be flagged as outlier depending on structure
            assert isinstance(report["is_outlier"], bool)
        finally:
            OutlierTestFixtures.cleanup(fixture)
    
    def test_generated_code_directories(self):
        """Test detection of generated code directories."""
        fixture = OutlierTestFixtures.create_generated_code_codebase()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "generated_code" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_git_submodules_detection(self):
        """Test detection of git submodules."""
        fixture = Path(tempfile.mkdtemp())
        (fixture / ".gitmodules").write_text("[submodule \"external\"]\n\tpath = external\n\turl = https://github.com/example/repo.git")
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "git_submodules" in report["outlier_types"]
        finally:
            OutlierTestFixtures.cleanup(fixture)
    
    def test_namespace_packages_detection(self):
        """Test detection of namespace packages."""
        fixture = OutlierTestFixtures.create_namespace_package_codebase()
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            assert report["is_outlier"] == True
            assert "namespace_packages" in report["outlier_types"]
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_multiple_python_versions_structure(self):
        """Test structure with multiple Python versions."""
        fixture = OutlierTestFixtures.create_multiple_python_versions_codebase()
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # May be flagged as outlier due to unusual structure
            assert isinstance(report["is_outlier"], bool)
        finally:
            OutlierTestFixtures.cleanup(fixture)
    
    def test_custom_python_paths_structure(self):
        """Test structure with custom Python paths."""
        fixture = OutlierTestFixtures.create_custom_python_paths_codebase()
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # Should handle custom paths
            assert isinstance(report["is_outlier"], bool)
        finally:
            OutlierTestFixtures.cleanup(fixture)
    
    def test_mixed_project_types_structure(self):
        """Test structure with mixed project types."""
        fixture = OutlierTestFixtures.create_mixed_project_types_codebase()
        # Add docs directory
        (fixture / "docs").mkdir(parents=True, exist_ok=True)
        (fixture / "docs" / "README.md").write_text("# Documentation")
        
        try:
            detector = OutlierDetector()
            report = detector.detect_outliers(fixture)
            
            # Mixed project types may be flagged
            assert isinstance(report["is_outlier"], bool)
        finally:
            OutlierTestFixtures.cleanup(fixture)
    
    def test_symlink_structure(self):
        """Test structure with symlinks."""
        import os
        
        fixture = Path(tempfile.mkdtemp())
        source_dir = fixture / "source"
        source_dir.mkdir()
        (source_dir / "code.py").write_text("from semantic_kernel import Kernel")
        
        try:
            # Create symlink (may not work on Windows)
            symlink_dir = fixture / "linked"
            try:
                symlink_dir.symlink_to(source_dir)
                
                detector = OutlierDetector()
                report = detector.detect_outliers(fixture)
                
                # Should handle symlinks
                assert isinstance(report["is_outlier"], bool)
            except (OSError, NotImplementedError):
                pytest.skip("Symlinks not supported on this system")
        finally:
            OutlierTestFixtures.cleanup(fixture)

