"""
Unit tests for metrics module.

Tests:
- Metrics calculation (transformation rate, error rates)
- Success criteria evaluation
- Metrics recording (analysis, transformation, validation)
- Display and export functionality
- Integration with validation results

Coverage target: >90%
"""

import pytest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from migratex.core.metrics import (
    MigrationMetrics,
    calculate_metrics_from_validation,
)
from migratex.validation import ValidationResult, ValidationError, ValidationLevel


class TestMigrationMetricsCreation:
    """Test MigrationMetrics creation and initialization."""
    
    def test_create_empty_metrics(self):
        """Test creating empty metrics object."""
        metrics = MigrationMetrics()
        
        assert metrics.total_files == 0
        assert metrics.files_analyzed == 0
        assert metrics.files_transformed == 0
        assert metrics.transformation_rate == 0.0
        assert metrics.start_time is not None
    
    def test_create_metrics_with_data(self):
        """Test creating metrics with initial data."""
        metrics = MigrationMetrics(
            total_files=100,
            files_analyzed=90,
            files_transformed=80
        )
        
        assert metrics.total_files == 100
        assert metrics.files_analyzed == 90
        assert metrics.files_transformed == 80
        assert metrics.transformation_rate > 0


class TestMetricsCalculations:
    """Test metrics calculations."""
    
    def test_transformation_rate_calculation(self):
        """Test transformation rate calculation."""
        metrics = MigrationMetrics(
            files_analyzed=100,
            files_transformed=80
        )
        
        assert metrics.transformation_rate == 80.0
    
    def test_transformation_rate_zero_files(self):
        """Test transformation rate with zero files."""
        metrics = MigrationMetrics()
        
        assert metrics.transformation_rate == 0.0
    
    def test_syntax_error_rate_calculation(self):
        """Test syntax error rate calculation."""
        metrics = MigrationMetrics(
            files_transformed=100,
            files_with_syntax_errors=5
        )
        
        assert metrics.syntax_error_rate == 5.0
    
    def test_import_error_rate_calculation(self):
        """Test import error rate calculation."""
        metrics = MigrationMetrics(
            files_transformed=100,
            files_with_import_errors=10
        )
        
        assert metrics.import_error_rate == 10.0
    
    def test_pattern_transformation_rate(self):
        """Test pattern transformation rate."""
        metrics = MigrationMetrics(
            patterns_detected=50,
            patterns_transformed=45
        )
        
        assert metrics.pattern_transformation_rate == 90.0
    
    def test_success_rate_calculation(self):
        """Test overall success rate calculation."""
        metrics = MigrationMetrics(
            files_transformed=100,
            files_with_syntax_errors=5,
            files_with_import_errors=10
        )
        
        # Success = 100 - 5 - 10 = 85
        assert metrics.success_rate == 85.0
    
    def test_duration_calculation(self):
        """Test duration calculation."""
        start = datetime.now()
        metrics = MigrationMetrics(start_time=start)
        
        # Duration should be calculated from start to now
        assert metrics.duration_seconds is not None
        assert metrics.duration_seconds >= 0


class TestSuccessCriteria:
    """Test success criteria evaluation."""
    
    def test_meets_transformation_rate_criteria(self):
        """Test transformation rate criteria (≥75%)."""
        # Meets criteria
        metrics1 = MigrationMetrics(files_analyzed=100, files_transformed=80)
        assert metrics1.meets_transformation_rate_criteria()
        
        # Below threshold
        metrics2 = MigrationMetrics(files_analyzed=100, files_transformed=70)
        assert not metrics2.meets_transformation_rate_criteria()
        
        # Exactly at threshold
        metrics3 = MigrationMetrics(files_analyzed=100, files_transformed=75)
        assert metrics3.meets_transformation_rate_criteria()
    
    def test_meets_syntax_error_criteria(self):
        """Test syntax error rate criteria (≤5%)."""
        # Meets criteria
        metrics1 = MigrationMetrics(files_transformed=100, files_with_syntax_errors=4)
        assert metrics1.meets_syntax_error_criteria()
        
        # Above threshold
        metrics2 = MigrationMetrics(files_transformed=100, files_with_syntax_errors=6)
        assert not metrics2.meets_syntax_error_criteria()
        
        # Exactly at threshold
        metrics3 = MigrationMetrics(files_transformed=100, files_with_syntax_errors=5)
        assert metrics3.meets_syntax_error_criteria()
    
    def test_meets_import_error_criteria(self):
        """Test import error rate criteria (≤10%)."""
        # Meets criteria
        metrics1 = MigrationMetrics(files_transformed=100, files_with_import_errors=8)
        assert metrics1.meets_import_error_criteria()
        
        # Above threshold
        metrics2 = MigrationMetrics(files_transformed=100, files_with_import_errors=12)
        assert not metrics2.meets_import_error_criteria()
        
        # Exactly at threshold
        metrics3 = MigrationMetrics(files_transformed=100, files_with_import_errors=10)
        assert metrics3.meets_import_error_criteria()
    
    def test_meets_all_success_criteria(self):
        """Test overall success criteria."""
        # Meets all criteria
        metrics_success = MigrationMetrics(
            files_analyzed=100,
            files_transformed=80,  # 80% ≥ 75%
            files_with_syntax_errors=4,  # 5% ≤ 5%
            files_with_import_errors=8  # 10% ≤ 10%
        )
        assert metrics_success.meets_success_criteria()
        
        # Fails transformation rate
        metrics_fail1 = MigrationMetrics(
            files_analyzed=100,
            files_transformed=70,  # 70% < 75%
            files_with_syntax_errors=4,
            files_with_import_errors=8
        )
        assert not metrics_fail1.meets_success_criteria()
        
        # Fails syntax error rate
        metrics_fail2 = MigrationMetrics(
            files_analyzed=100,
            files_transformed=80,
            files_with_syntax_errors=6,  # 7.5% > 5%
            files_with_import_errors=8
        )
        assert not metrics_fail2.meets_success_criteria()
        
        # Fails import error rate
        metrics_fail3 = MigrationMetrics(
            files_analyzed=100,
            files_transformed=80,
            files_with_syntax_errors=4,
            files_with_import_errors=12  # 15% > 10%
        )
        assert not metrics_fail3.meets_success_criteria()
    
    def test_get_success_criteria_status(self):
        """Test getting success criteria status dict."""
        metrics = MigrationMetrics(
            files_analyzed=100,
            files_transformed=80,
            files_with_syntax_errors=4,
            files_with_import_errors=8
        )
        
        status = metrics.get_success_criteria_status()
        
        assert isinstance(status, dict)
        assert status['transformation_rate'] is True
        assert status['syntax_error_rate'] is True
        assert status['import_error_rate'] is True
        assert status['overall'] is True


class TestMetricsRecording:
    """Test recording metrics from different phases."""
    
    def test_record_analysis(self):
        """Test recording analysis phase metrics."""
        metrics = MigrationMetrics()
        
        metrics.record_analysis(
            files_analyzed=100,
            patterns_detected=50
        )
        
        assert metrics.files_analyzed == 100
        assert metrics.patterns_detected == 50
    
    def test_record_transformation(self):
        """Test recording transformation phase metrics."""
        metrics = MigrationMetrics()
        
        metrics.record_transformation(
            files_transformed=80,
            patterns_transformed=45,
            transformation_errors=2
        )
        
        assert metrics.files_transformed == 80
        assert metrics.patterns_transformed == 45
        assert metrics.transformation_errors == 2
    
    def test_record_validation(self):
        """Test recording validation phase metrics."""
        metrics = MigrationMetrics()
        
        metrics.record_validation(
            files_with_syntax_errors=4,
            files_with_import_errors=8,
            validation_errors=1
        )
        
        assert metrics.files_with_syntax_errors == 4
        assert metrics.files_with_import_errors == 8
        assert metrics.validation_errors == 1
    
    def test_finish_metrics(self):
        """Test finishing metrics collection."""
        metrics = MigrationMetrics()
        
        assert metrics.end_time is None
        
        metrics.finish()
        
        assert metrics.end_time is not None
        assert metrics.duration_seconds is not None


class TestMetricsExport:
    """Test metrics export functionality."""
    
    def test_to_dict(self):
        """Test converting metrics to dict."""
        metrics = MigrationMetrics(
            total_files=100,
            files_analyzed=90,
            files_transformed=80
        )
        
        data = metrics.to_dict()
        
        assert isinstance(data, dict)
        assert data['total_files'] == 100
        assert data['files_analyzed'] == 90
        assert data['files_transformed'] == 80
        assert 'calculated' in data
        assert 'success_criteria' in data
    
    def test_to_json(self):
        """Test converting metrics to JSON."""
        metrics = MigrationMetrics(
            total_files=100,
            files_analyzed=90
        )
        
        json_str = metrics.to_json()
        
        assert isinstance(json_str, str)
        assert '"total_files": 100' in json_str
        assert '"files_analyzed": 90' in json_str
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading metrics."""
        # Create metrics
        metrics_original = MigrationMetrics(
            total_files=100,
            files_analyzed=90,
            files_transformed=80,
            patterns_detected=50,
            patterns_transformed=45
        )
        
        # Save to file
        file_path = tmp_path / "metrics.json"
        metrics_original.save(file_path)
        
        assert file_path.exists()
        
        # Load from file
        metrics_loaded = MigrationMetrics.load(file_path)
        
        assert metrics_loaded.total_files == 100
        assert metrics_loaded.files_analyzed == 90
        assert metrics_loaded.files_transformed == 80
        assert metrics_loaded.patterns_detected == 50
        assert metrics_loaded.patterns_transformed == 45


class TestCalculateMetricsFromValidation:
    """Test calculating metrics from validation results."""
    
    def test_calculate_from_validation_results(self):
        """Test calculating metrics from validation results."""
        # Create mock validation results
        validation_results = {}
        
        # Valid file
        validation_results["file1.py"] = ValidationResult(
            file_path="file1.py",
            is_valid=True
        )
        
        # File with syntax error
        result2 = ValidationResult(file_path="file2.py", is_valid=False)
        result2.add_error(ValidationError(
            level=ValidationLevel.ERROR,
            file_path="file2.py",
            line_number=10,
            column_number=5,
            error_type="SyntaxError",
            message="Invalid syntax"
        ))
        validation_results["file2.py"] = result2
        
        # File with import error
        result3 = ValidationResult(file_path="file3.py", is_valid=False)
        result3.add_error(ValidationError(
            level=ValidationLevel.WARNING,
            file_path="file3.py",
            line_number=5,
            column_number=None,
            error_type="ImportWarning",
            message="Cannot resolve import"
        ))
        validation_results["file3.py"] = result3
        
        # Calculate metrics
        metrics = calculate_metrics_from_validation(validation_results, total_files=100)
        
        assert metrics.files_analyzed == 3
        assert metrics.files_transformed == 3
        assert metrics.files_with_syntax_errors > 0
        assert metrics.files_with_import_errors > 0


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_successful_migration_scenario(self):
        """Test metrics for successful migration."""
        metrics = MigrationMetrics()
        
        # Record analysis
        metrics.record_analysis(files_analyzed=100, patterns_detected=80)
        
        # Record transformation
        metrics.record_transformation(
            files_transformed=85,
            patterns_transformed=75,
            transformation_errors=0
        )
        
        # Record validation
        metrics.record_validation(
            files_with_syntax_errors=2,
            files_with_import_errors=5,
            validation_errors=0
        )
        
        metrics.finish()
        
        # Check success
        assert metrics.meets_success_criteria()
        assert metrics.transformation_rate >= 75.0
        assert metrics.syntax_error_rate <= 5.0
        assert metrics.import_error_rate <= 10.0
    
    def test_failed_migration_scenario(self):
        """Test metrics for failed migration."""
        metrics = MigrationMetrics()
        
        # Record analysis
        metrics.record_analysis(files_analyzed=100, patterns_detected=80)
        
        # Record transformation (low success rate)
        metrics.record_transformation(
            files_transformed=60,  # Only 60% transformed
            patterns_transformed=40,
            transformation_errors=10
        )
        
        # Record validation (high error rates)
        metrics.record_validation(
            files_with_syntax_errors=10,  # 16.7% error rate
            files_with_import_errors=15,  # 25% error rate
            validation_errors=5
        )
        
        metrics.finish()
        
        # Check failure
        assert not metrics.meets_success_criteria()
        assert not metrics.meets_transformation_rate_criteria()
        assert not metrics.meets_syntax_error_criteria()
        assert not metrics.meets_import_error_criteria()

