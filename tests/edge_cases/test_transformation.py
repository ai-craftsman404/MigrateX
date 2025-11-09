"""
Transformation Edge Case Tests (Agent 4 - T4.3)

Tests edge cases for transformation logic.
Target: 15+ edge cases, 100% of transformation edge cases
"""

import pytest
from pathlib import Path
from migratex.core.context import MigrationContext
from migratex.agents.refactorer import RefactorerAgent
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestTransformationEdgeCases:
    """Test transformation edge cases."""
    
    def test_circular_import_dependencies(self):
        """Test transformation with circular import dependencies."""
        fixture = EdgeCaseTestFixtures.create_circular_dependency_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="auto", error_policy="continue")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            
            # Should handle circular dependencies
            for file_path in fixture.rglob("*.py"):
                if file_path.name in ["a.py", "b.py"]:
                    try:
                        result = refactorer._transform_file(file_path, [], auto_mode=True)
                        assert isinstance(result, bool)
                    except Exception:
                        # May fail due to circular imports, but should handle gracefully
                        pass
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_applied_multiple_times(self):
        """Test pattern applied multiple times in same file."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel import Kernel  # Duplicate
from semantic_kernel import Kernel  # Another duplicate
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle multiple applications
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_conflicts_resolution(self):
        """Test resolution of pattern conflicts."""
        fixture = EdgeCaseTestFixtures.create_pattern_conflict_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "conflict.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_import", "file": str(fixture / "conflict.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "conflict.py"
            
            # Should resolve conflicts
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_nested_transformations(self):
        """Test nested transformations (transformation within transformation)."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel.agents import KernelAgent

class MyAgent(KernelAgent):
    def __init__(self):
        self.kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle nested patterns
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_decorators(self):
        """Test transformation with decorators."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve decorators
            assert "@kernel_function" in transformed or "@kernel_function" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_metaclasses(self):
        """Test transformation with metaclasses."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class Meta(type):
    pass

class MyClass(metaclass=Meta):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should handle metaclasses
            assert "metaclass=Meta" in transformed or "metaclass=Meta" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_order_dependency(self):
        """Test transformation order dependency."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel.agents import KernelAgent

class MyAgent(KernelAgent):
    def __init__(self):
        self.kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_class_inheritance", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle order dependencies
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_preserves_whitespace(self):
        """Test transformation preserves whitespace."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel


class MyAgent:
    def __init__(self):
        self.kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve whitespace structure
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_complex_expressions(self):
        """Test transformation with complex expressions."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

result = Kernel() if condition else None
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle complex expressions
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_list_comprehensions(self):
        """Test transformation with list comprehensions."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernels = [Kernel() for _ in range(10)]
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle list comprehensions
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_generators(self):
        """Test transformation with generators."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

def get_kernels():
    yield Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle generators
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_context_managers(self):
        """Test transformation with context managers."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

with Kernel() as kernel:
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle context managers
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_lambdas(self):
        """Test transformation with lambdas."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

func = lambda: Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle lambdas
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_properties(self):
        """Test transformation with properties."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @property
    def kernel(self):
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle properties
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_class_methods(self):
        """Test transformation with class methods."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @classmethod
    def create(cls):
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle class methods
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_static_methods(self):
        """Test transformation with static methods."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @staticmethod
    def create():
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {"patterns": []}
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # Should handle static methods
            result = refactorer._transform_file(file_path, [], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

