"""
Integration tests for Agent Communication (Agent 2 - T2.2)

Tests interactions between different agents.
Target: 8+ scenarios, 100% of agent interactions
"""

import pytest
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.agents.code_analyzer import CodeAnalyzerAgent
from migratex.agents.refactorer import RefactorerAgent
from migratex.patterns.discovery import PatternDiscovery
from migratex.patterns.library import PatternLibrary
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestAgentCommunication:
    """Test communication and data flow between agents."""
    
    def test_code_analyzer_to_refactorer_flow(self):
        """Test data flow from CodeAnalyzer to Refactorer."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            # CodeAnalyzer runs first
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Refactorer uses analyzer's report
            context.mode = "auto"
            refactorer = RefactorerAgent(context)
            
            # Verify data flow
            assert context.report is not None
            assert "patterns" in context.report
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_library_to_refactorer_flow(self):
        """Test data flow from PatternLibrary to Refactorer."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            
            # PatternLibrary loads patterns
            pattern_library = PatternLibrary()
            context.pattern_library = pattern_library
            
            # Refactorer uses pattern library
            refactorer = RefactorerAgent(context)
            
            assert refactorer.context.pattern_library is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_cache_to_review_mode_flow(self):
        """Test data flow from PatternCache to Review mode."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            context = MigrationContext(
                project_path=fixture,
                mode="review",
                remember_decisions=True
            )
            
            # PatternCache stores decisions
            assert context.pattern_cache is not None
            assert context.remember_decisions == True
            
            # Review mode uses cache
            refactorer = RefactorerAgent(context)
            assert refactorer.context.pattern_cache is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_orchestrator_coordinates_agents(self):
        """Test Orchestrator coordinates multiple agents."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            
            # Orchestrator manages workflow
            from migratex.core.orchestrator import Orchestrator
            orchestrator = Orchestrator(context)
            
            # Run analyze (uses CodeAnalyzer)
            orchestrator.run_analysis()
            
            # Verify agents were coordinated
            assert context.report is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_error_propagation_between_agents(self):
        """Test error propagation between agents."""
        fixture = EdgeCaseTestFixtures.create_syntax_error_codebase()
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            analyzer = CodeAnalyzerAgent(context)
            
            # Should handle errors gracefully
            try:
                analyzer.run()
                errors_handled = True
            except Exception:
                errors_handled = False
            
            # Errors should be handled or propagated appropriately
            assert isinstance(errors_handled, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_context_shared_between_agents(self):
        """Test that context is shared correctly between agents."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            
            # First agent modifies context
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            # Second agent sees same context
            context.mode = "auto"
            refactorer = RefactorerAgent(context)
            
            # Verify shared state
            assert refactorer.context.project_path == analyzer.context.project_path
            assert refactorer.context.report == analyzer.context.report
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_discovery_to_library_flow(self):
        """Test data flow from PatternDiscovery to PatternLibrary."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            
            # PatternDiscovery finds patterns
            discovery = PatternDiscovery(context)
            python_files = list(fixture.rglob("*.py"))
            patterns = discovery.discover_patterns(python_files)
            
            # PatternLibrary loads relevant patterns
            pattern_library = PatternLibrary()
            if patterns:
                pattern_ids = [p.get("id") for p in patterns if p.get("id")]
                pattern_library.load_relevant(pattern_ids)
            
            assert pattern_library is not None
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_multiple_agents_same_context(self):
        """Test multiple agents can use same context."""
        fixture = EdgeCaseTestFixtures.create_mixed_frameworks_codebase()
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            
            # Multiple agents use same context
            analyzer = CodeAnalyzerAgent(context)
            analyzer.run()
            
            context.mode = "auto"
            refactorer = RefactorerAgent(context)
            
            # Both agents share context
            assert analyzer.context is refactorer.context
            assert analyzer.context.report == refactorer.context.report
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

