"""
Pattern mapping verification tests - CRITICAL for ensuring one-to-one pattern-to-transformation mapping.
"""

import pytest
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.core.orchestrator import Orchestrator
from migratex.testing.pattern_mapping_verification import (
    verify_pattern_application_mapping,
    verify_pattern_output_mapping,
    generate_complete_pattern_mapping_report
)


class TestPatternMappingVerification:
    """Test pattern-to-transformation mapping verification."""
    
    def test_pattern_application_mapping_basic(self, temp_codebase):
        """Test basic pattern application mapping."""
        context = MigrationContext(project_path=temp_codebase, mode="analyze", verbose=True)
        orchestrator = Orchestrator(context)
        
        # Run analysis
        orchestrator.run_analysis()
        
        # Run transformation
        context.mode = "auto"
        orchestrator.run_apply_auto()
        
        # Verify pattern application mapping
        result = verify_pattern_application_mapping(context)
        
        # CRITICAL: If patterns detected, must have transformations
        if result["total_detected"] > 0:
            assert result["total_applied"] > 0 or result["total_files_transformed"] > 0, \
                f"CRITICAL: {result['total_detected']} patterns detected but 0 applied and 0 files transformed"
            assert result["mapping_complete"], \
                f"CRITICAL: Pattern mapping incomplete. Failed patterns: {result['failed_patterns']}"
    
    def test_pattern_output_mapping_basic(self, temp_codebase):
        """Test basic pattern output mapping."""
        context = MigrationContext(project_path=temp_codebase, mode="analyze", verbose=True)
        orchestrator = Orchestrator(context)
        
        # Run analysis
        orchestrator.run_analysis()
        
        # Run transformation
        context.mode = "auto"
        orchestrator.run_apply_auto()
        
        # Verify pattern output mapping
        output_map = verify_pattern_output_mapping(context)
        
        # CRITICAL: Check for failed transformations
        failed_outputs = [m for m in output_map if m["status"] == "failed"]
        assert len(failed_outputs) == 0, \
            f"CRITICAL: {len(failed_outputs)} pattern transformations failed: {failed_outputs}"
    
    def test_complete_pattern_mapping_report(self, temp_codebase):
        """Test complete pattern mapping report generation."""
        context = MigrationContext(project_path=temp_codebase, mode="analyze", verbose=True)
        orchestrator = Orchestrator(context)
        
        # Run analysis
        orchestrator.run_analysis()
        
        # Run transformation
        context.mode = "auto"
        orchestrator.run_apply_auto()
        
        # Generate complete report
        report = generate_complete_pattern_mapping_report(context)
        
        # CRITICAL: Verify report structure
        assert "summary" in report
        assert "pattern_application_mapping" in report
        assert "pattern_output_mapping" in report
        assert "failed_patterns" in report
        assert "mapping_complete" in report
        
        # CRITICAL: If patterns detected, mapping must be complete
        if report["summary"]["high_confidence_patterns"] > 0:
            assert report["mapping_complete"], \
                f"CRITICAL: Pattern mapping incomplete. Failed: {report['failed_patterns']}"
    
    def test_pattern_mapping_with_real_sk_code(self, sample_sk_codebase):
        """Test pattern mapping with real SK code."""
        context = MigrationContext(project_path=sample_sk_codebase, mode="analyze", verbose=True)
        orchestrator = Orchestrator(context)
        
        # Run analysis
        orchestrator.run_analysis()
        detected_patterns = context.report.get("patterns", [])
        high_confidence = [
            p for p in detected_patterns 
            if p.get("confidence") == "high" and p.get("source") == "rule"
        ]
        
        if len(high_confidence) == 0:
            pytest.skip("No high-confidence patterns detected")
        
        # Run transformation
        context.mode = "auto"
        orchestrator.run_apply_auto()
        
        # Verify mapping
        result = verify_pattern_application_mapping(context)
        
        # CRITICAL: Must have transformations if patterns detected
        assert result["total_applied"] > 0 or result["total_files_transformed"] > 0, \
            f"CRITICAL: {result['total_detected']} patterns detected but 0 transformations"
        
        # Verify output mapping
        output_map = verify_pattern_output_mapping(context)
        failed = [m for m in output_map if m["status"] == "failed"]
        assert len(failed) == 0, f"CRITICAL: {len(failed)} transformations failed"
    
    def test_pattern_mapping_verification_in_e2e(self, sample_sk_codebase):
        """Test pattern mapping verification in E2E scenario."""
        context = MigrationContext(
            project_path=sample_sk_codebase,
            mode="analyze",
            verbose=True,
            use_git_branch=False  # Don't require git for this test
        )
        orchestrator = Orchestrator(context)
        
        # Run analysis
        orchestrator.run_analysis()
        
        # Run transformation
        context.mode = "auto"
        orchestrator.run_apply_auto()
        
        # Generate mapping report
        report = generate_complete_pattern_mapping_report(context)
        
        # CRITICAL: Verify mapping completeness
        if report["summary"]["high_confidence_patterns"] > 0:
            assert report["mapping_complete"], \
                f"CRITICAL: E2E pattern mapping incomplete: {report['failed_patterns']}"
            
            # Verify transformation success rate
            success_rate = report["summary"]["transformation_success_rate"]
            assert success_rate > 0, \
                f"CRITICAL: Transformation success rate is 0%"

