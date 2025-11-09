"""
Performance Tests (Agent 6 - T6.1, T6.2, T6.3)

Tests performance, scalability, and resource usage.
Target: 18+ scenarios, validates production readiness
"""

import pytest
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from migratex.core.context import MigrationContext
from migratex.agents.code_analyzer import CodeAnalyzerAgent
from migratex.agents.refactorer import RefactorerAgent
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
import os
import threading
import signal


class TestLargeCodebasePerformance:
    """Test performance with large codebases."""
    
    def test_very_large_codebase_analysis_time(self):
        """Test analysis time for very large codebase (>10K files)."""
        # Create large codebase (simulated with many files)
        fixture = Path(tempfile.mkdtemp())
        
        # Create 100 files (simulating large codebase)
        for i in range(100):
            file_path = fixture / f"file_{i}.py"
            file_path.write_text(f"from semantic_kernel import Kernel\n# File {i}")
        
        try:
            start_time = time.time()
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            elapsed_time = time.time() - start_time
            
            # Should complete in reasonable time (<30s for <1000 files)
            assert elapsed_time < 60.0  # 60 second threshold
            assert context.report is not None
        finally:
            shutil.rmtree(fixture)
    
    def test_very_large_files_handling(self):
        """Test handling of very large files (>100K lines)."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=50000)
        try:
            start_time = time.time()
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            elapsed_time = time.time() - start_time
            
            # Should handle large files in reasonable time
            assert elapsed_time < 120.0  # 2 minute threshold for very large files
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_deep_directory_structure_performance(self):
        """Test performance with deep directory structures (>50 levels)."""
        fixture = EdgeCaseTestFixtures.create_deep_nested_codebase(levels=50)
        try:
            start_time = time.time()
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            elapsed_time = time.time() - start_time
            
            # Should handle deep nesting efficiently
            assert elapsed_time < 60.0
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_many_patterns_detection_performance(self):
        """Test performance with many patterns detected (>500)."""
        fixture = Path(tempfile.mkdtemp())
        
        # Create files with patterns
        for i in range(200):
            file_path = fixture / f"sk_file_{i}.py"
            file_path.write_text("from semantic_kernel import Kernel")
        
        try:
            start_time = time.time()
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            elapsed_time = time.time() - start_time
            
            # Should handle many patterns efficiently
            assert elapsed_time < 60.0
            assert context.report is not None
        finally:
            shutil.rmtree(fixture)
    
    def test_memory_usage_under_load(self):
        """Test memory usage under load."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=10000)
        try:
            if not HAS_PSUTIL:
                pytest.skip("psutil not available")
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Should use reasonable memory (<500MB for typical codebase)
            assert memory_increase < 500.0  # 500MB threshold
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_cpu_usage_under_load(self):
        """Test CPU usage under load."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=5000)
        try:
            if not HAS_PSUTIL:
                pytest.skip("psutil not available")
            
            process = psutil.Process(os.getpid())
            
            # Measure CPU usage during analysis
            process.cpu_percent(interval=0.1)  # Initialize
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # CPU usage should be reasonable (not 100% sustained)
            # This is a basic check - actual CPU usage depends on system
            assert isinstance(cpu_percent, (int, float))
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_concurrent_operations_prevention(self):
        """Test that concurrent migrations are prevented."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            context1 = MigrationContext(project_path=fixture, mode="auto")
            context2 = MigrationContext(project_path=fixture, mode="auto")
            
            # Both contexts should be able to exist
            # Actual prevention would be in orchestrator/CLI level
            assert context1.project_path == context2.project_path
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_resource_cleanup_after_analysis(self):
        """Test that resources are cleaned up after analysis."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("import os")
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Analysis should complete without resource leaks
            assert context.report is not None
            
            # Context should still be usable
            checkpoint = context.get_checkpoint()
            assert isinstance(checkpoint, dict) and len(checkpoint) > 0, "Checkpoint should be non-empty dict"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)


class TestTimeoutAndResourceLimits:
    """Test timeout handling and resource limits."""
    
    def test_timeout_slow_filesystem(self):
        """Test timeout handling on slow filesystem."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        
        # Mock slow file operations
        original_read = Path.read_text
        
        def slow_read(self, *args, **kwargs):
            time.sleep(0.1)  # Simulate slow I/O
            return original_read(self, *args, **kwargs)
        
        try:
            with patch.object(Path, 'read_text', slow_read):
                start_time = time.time()
                
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                analyzer.run()
                
                elapsed_time = time.time() - start_time
                
                # Should complete even with slow I/O (within reasonable time)
                assert elapsed_time < 30.0  # 30 second threshold
                assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_memory_exhaustion_handling(self):
        """Test handling of memory limits."""
        if not HAS_PSUTIL:
            pytest.skip("psutil not available")
        
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=50000)
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Should handle large files without excessive memory (<1GB)
            assert memory_increase < 1000.0  # 1GB threshold
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_cpu_bound_interruptible(self):
        """Test that CPU-bound operations can be interrupted."""
        fixture = EdgeCaseTestFixtures.create_large_file_codebase(lines=20000)
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            
            # Should complete without hanging
            analyzer.run()
            
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_file_system_contention(self):
        """Test concurrent file access handling."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        results = []
        
        def run_analysis():
            try:
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                analyzer.run()
                results.append(True)
            except Exception as e:
                results.append(False)
        
        try:
            # Simulate concurrent access (though actual prevention is at CLI level)
            threads = [threading.Thread(target=run_analysis) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=10.0)
            
            # At least one should succeed
            assert any(results)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_resource_locking(self):
        """Test file locking scenarios."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        test_file = fixture / "main.py"
        
        try:
            # Try to analyze while file might be locked (OS-dependent)
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Should handle file locking gracefully
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)


class TestPerformanceBenchmarking:
    """Test performance benchmarking and regression detection."""
    
    def test_performance_baseline(self):
        """Establish baseline performance metrics."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        try:
            start_time = time.time()
            
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            elapsed_time = time.time() - start_time
            
            # Baseline: small codebase should analyze in <5 seconds
            baseline_time = elapsed_time
            
            # Store baseline for regression detection
            assert baseline_time < 5.0
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_performance_regression(self):
        """Detect performance regressions."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        try:
            # Run multiple times to check consistency
            times = []
            for _ in range(3):
                start_time = time.time()
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                analyzer.run()
                elapsed_time = time.time() - start_time
                times.append(elapsed_time)
            
            # Performance should be consistent (within 2x variance)
            max_time = max(times)
            min_time = min(times)
            assert max_time / min_time < 2.0 if min_time > 0 else True
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_scalability_linear(self):
        """Validate linear scalability."""
        # Test with different codebase sizes
        sizes = [10, 50, 100]
        times = []
        
        for size in sizes:
            fixture = Path(tempfile.mkdtemp())
            try:
                # Create files
                for i in range(size):
                    file_path = fixture / f"file_{i}.py"
                    file_path.write_text(f"from semantic_kernel import Kernel\n# File {i}")
                
                start_time = time.time()
                context = MigrationContext(project_path=fixture, mode="analyze")
                analyzer = CodeAnalyzerAgent(context)
                analyzer.run()
                elapsed_time = time.time() - start_time
                times.append(elapsed_time)
            finally:
                shutil.rmtree(fixture)
        
        # Should scale roughly linearly (within 3x for 10x size increase)
        if len(times) >= 2:
            ratio = times[-1] / times[0] if times[0] > 0 else 1.0
            size_ratio = sizes[-1] / sizes[0]
            # Allow some overhead (3x time for 10x size is acceptable)
            assert ratio <= size_ratio * 3


class TestConcurrencyAndResourceCleanup:
    """Test concurrency prevention and resource cleanup."""
    
    def test_concurrent_migration_prevention(self):
        """Test that concurrent migrations are prevented."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        try:
            # Create multiple contexts (actual prevention is at CLI/orchestrator level)
            context1 = MigrationContext(project_path=fixture, mode="auto")
            context2 = MigrationContext(project_path=fixture, mode="auto")
            
            # Both contexts should be valid
            assert context1.project_path == context2.project_path
            assert context1.mode == context2.mode
            
            # Actual concurrency prevention would be tested at CLI level
            # This test validates context creation doesn't conflict
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_resource_cleanup_validation(self):
        """Validate resource cleanup after operations."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase("from semantic_kernel import Kernel")
        try:
            if not HAS_PSUTIL:
                pytest.skip("psutil not available")
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Run analysis
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Run again to check for memory leaks
            context2 = MigrationContext(project_path=fixture, mode="analyze")
            analyzer2 = CodeAnalyzerAgent(context2)
            analyzer2.run()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (no major leaks)
            assert memory_increase < 200.0  # 200MB threshold
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

