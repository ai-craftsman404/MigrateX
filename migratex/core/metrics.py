"""
Migration Metrics Module

Calculates and tracks metrics for migration success:
- Transformation rate (% of files transformed)
- Syntax error rate (% of files with syntax errors)
- Import error rate (% of files with import errors)
- Success criteria evaluation

Architecture:
- Integrates with migration workflow
- Uses runtime validation results
- Provides CLI-friendly display
- Saves metrics to reports

Usage:
    from migratex.core.metrics import MigrationMetrics
    
    metrics = MigrationMetrics()
    metrics.record_migration(
        total_files=100,
        files_transformed=85,
        syntax_errors=2,
        import_errors=5
    )
    
    if metrics.meets_success_criteria():
        print("✅ Migration successful!")
    else:
        print("❌ Migration did not meet success criteria")
    
    metrics.display()
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json


@dataclass
class MigrationMetrics:
    """
    Tracks migration metrics and evaluates success criteria.
    
    Success Criteria (from VALIDATION_ACCEPTANCE_CRITERIA.md):
    - Transformation rate ≥ 75%
    - Syntax error rate ≤ 5%
    - Import error rate ≤ 10%
    """
    
    # Core metrics
    total_files: int = 0
    files_analyzed: int = 0
    files_transformed: int = 0
    files_with_syntax_errors: int = 0
    files_with_import_errors: int = 0
    files_skipped: int = 0
    
    # Pattern metrics
    patterns_detected: int = 0
    patterns_transformed: int = 0
    
    # Error metrics
    transformation_errors: int = 0
    validation_errors: int = 0
    
    # Time metrics
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Success criteria thresholds
    min_transformation_rate: float = 75.0  # %
    max_syntax_error_rate: float = 5.0     # %
    max_import_error_rate: float = 10.0    # %
    
    # Additional data
    repository_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize start time if not set."""
        if self.start_time is None:
            self.start_time = datetime.now()
    
    # Calculated properties
    
    @property
    def transformation_rate(self) -> float:
        """Calculate transformation rate (% of files transformed)."""
        if self.files_analyzed == 0:
            return 0.0
        return (self.files_transformed / self.files_analyzed) * 100
    
    @property
    def syntax_error_rate(self) -> float:
        """Calculate syntax error rate (% of files with syntax errors)."""
        if self.files_transformed == 0:
            return 0.0
        return (self.files_with_syntax_errors / self.files_transformed) * 100
    
    @property
    def import_error_rate(self) -> float:
        """Calculate import error rate (% of files with import errors)."""
        if self.files_transformed == 0:
            return 0.0
        return (self.files_with_import_errors / self.files_transformed) * 100
    
    @property
    def pattern_transformation_rate(self) -> float:
        """Calculate pattern transformation rate."""
        if self.patterns_detected == 0:
            return 0.0
        return (self.patterns_transformed / self.patterns_detected) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.files_transformed == 0:
            return 0.0
        
        successful_files = (
            self.files_transformed 
            - self.files_with_syntax_errors 
            - self.files_with_import_errors
        )
        return (successful_files / self.files_transformed) * 100
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.start_time is None:
            return None
        
        end = self.end_time or datetime.now()
        delta = end - self.start_time
        return delta.total_seconds()
    
    # Success criteria evaluation
    
    def meets_transformation_rate_criteria(self) -> bool:
        """Check if transformation rate meets criteria."""
        return self.transformation_rate >= self.min_transformation_rate
    
    def meets_syntax_error_criteria(self) -> bool:
        """Check if syntax error rate meets criteria."""
        return self.syntax_error_rate <= self.max_syntax_error_rate
    
    def meets_import_error_criteria(self) -> bool:
        """Check if import error rate meets criteria."""
        return self.import_error_rate <= self.max_import_error_rate
    
    def meets_success_criteria(self) -> bool:
        """Check if all success criteria are met."""
        return (
            self.meets_transformation_rate_criteria() and
            self.meets_syntax_error_criteria() and
            self.meets_import_error_criteria()
        )
    
    def get_success_criteria_status(self) -> Dict[str, bool]:
        """Get status of all success criteria."""
        return {
            'transformation_rate': self.meets_transformation_rate_criteria(),
            'syntax_error_rate': self.meets_syntax_error_criteria(),
            'import_error_rate': self.meets_import_error_criteria(),
            'overall': self.meets_success_criteria(),
        }
    
    # Data recording
    
    def record_analysis(self, files_analyzed: int, patterns_detected: int) -> None:
        """Record analysis phase metrics."""
        self.files_analyzed = files_analyzed
        self.patterns_detected = patterns_detected
    
    def record_transformation(
        self, 
        files_transformed: int, 
        patterns_transformed: int,
        transformation_errors: int = 0
    ) -> None:
        """Record transformation phase metrics."""
        self.files_transformed = files_transformed
        self.patterns_transformed = patterns_transformed
        self.transformation_errors = transformation_errors
    
    def record_validation(
        self,
        files_with_syntax_errors: int,
        files_with_import_errors: int,
        validation_errors: int = 0
    ) -> None:
        """Record validation phase metrics."""
        self.files_with_syntax_errors = files_with_syntax_errors
        self.files_with_import_errors = files_with_import_errors
        self.validation_errors = validation_errors
    
    def finish(self) -> None:
        """Mark metrics collection as finished."""
        self.end_time = datetime.now()
    
    # Display and export
    
    def display(self, verbose: bool = False) -> None:
        """Display metrics in CLI-friendly format."""
        print("\n" + "=" * 80)
        print("MIGRATION METRICS")
        print("=" * 80)
        
        # Core metrics
        print(f"\n[CORE METRICS]:")
        print(f"  Total Files:          {self.total_files}")
        print(f"  Files Analyzed:       {self.files_analyzed}")
        print(f"  Files Transformed:    {self.files_transformed}")
        print(f"  Files Skipped:        {self.files_skipped}")
        
        # Rates
        print(f"\n[RATES]:")
        print(f"  Transformation Rate:  {self.transformation_rate:.1f}% ", end="")
        if self.meets_transformation_rate_criteria():
            print(f"[PASS] (>={self.min_transformation_rate}%)")
        else:
            print(f"[FAIL] (<{self.min_transformation_rate}%)")
        
        print(f"  Syntax Error Rate:    {self.syntax_error_rate:.1f}% ", end="")
        if self.meets_syntax_error_criteria():
            print(f"[PASS] (<={self.max_syntax_error_rate}%)")
        else:
            print(f"[FAIL] (>{self.max_syntax_error_rate}%)")
        
        print(f"  Import Error Rate:    {self.import_error_rate:.1f}% ", end="")
        if self.meets_import_error_criteria():
            print(f"[PASS] (<={self.max_import_error_rate}%)")
        else:
            print(f"[FAIL] (>{self.max_import_error_rate}%)")
        
        print(f"  Overall Success:      {self.success_rate:.1f}%")
        
        # Patterns
        if self.patterns_detected > 0:
            print(f"\n[PATTERN METRICS]:")
            print(f"  Patterns Detected:    {self.patterns_detected}")
            print(f"  Patterns Transformed: {self.patterns_transformed}")
            print(f"  Pattern Success Rate: {self.pattern_transformation_rate:.1f}%")
        
        # Errors
        if self.transformation_errors > 0 or self.validation_errors > 0:
            print(f"\n[ERRORS]:")
            print(f"  Transformation Errors: {self.transformation_errors}")
            print(f"  Validation Errors:     {self.validation_errors}")
        
        # Time
        if self.duration_seconds is not None:
            print(f"\n[DURATION]: {self.duration_seconds:.2f}s")
        
        # Success criteria
        print(f"\n[SUCCESS CRITERIA]:")
        criteria = self.get_success_criteria_status()
        for criterion, met in criteria.items():
            status = "[PASS]" if met else "[FAIL]"
            print(f"  {criterion.replace('_', ' ').title()}: {status}")
        
        print("=" * 80 + "\n")
        
        # Verbose details
        if verbose and self.metadata:
            print("Additional Metadata:")
            for key, value in self.metadata.items():
                print(f"  {key}: {value}")
            print()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        data = asdict(self)
        
        # Add calculated properties
        data['calculated'] = {
            'transformation_rate': self.transformation_rate,
            'syntax_error_rate': self.syntax_error_rate,
            'import_error_rate': self.import_error_rate,
            'pattern_transformation_rate': self.pattern_transformation_rate,
            'success_rate': self.success_rate,
            'duration_seconds': self.duration_seconds,
        }
        
        # Add success criteria status
        data['success_criteria'] = self.get_success_criteria_status()
        
        # Convert datetime objects to ISO format
        if data['start_time']:
            data['start_time'] = data['start_time'].isoformat()
        if data['end_time']:
            data['end_time'] = data['end_time'].isoformat()
        
        return data
    
    def to_json(self, indent: int = 2) -> str:
        """Convert metrics to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, file_path: Path) -> None:
        """Save metrics to JSON file."""
        file_path = Path(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, file_path: Path) -> 'MigrationMetrics':
        """Load metrics from JSON file."""
        file_path = Path(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Remove calculated fields
        data.pop('calculated', None)
        data.pop('success_criteria', None)
        
        # Convert datetime strings back to objects
        if data.get('start_time'):
            data['start_time'] = datetime.fromisoformat(data['start_time'])
        if data.get('end_time'):
            data['end_time'] = datetime.fromisoformat(data['end_time'])
        
        return cls(**data)


# Convenience functions

def calculate_metrics_from_validation(
    validation_results: Dict[str, Any],
    total_files: int = 0
) -> MigrationMetrics:
    """
    Calculate metrics from validation results.
    
    Args:
        validation_results: Dict of validation results
        total_files: Total number of files (optional)
        
    Returns:
        MigrationMetrics object
    """
    metrics = MigrationMetrics(total_files=total_files)
    
    # Count errors
    syntax_errors = 0
    import_errors = 0
    
    for file_path, result in validation_results.items():
        if not result.is_valid:
            # Check error types
            for error in result.errors:
                if 'syntax' in error.error_type.lower():
                    syntax_errors += 1
                    break
            
            for error in result.errors + result.warnings:
                if 'import' in error.error_type.lower():
                    import_errors += 1
                    break
    
    metrics.files_analyzed = len(validation_results)
    metrics.files_transformed = len(validation_results)
    metrics.files_with_syntax_errors = syntax_errors
    metrics.files_with_import_errors = import_errors
    
    return metrics

