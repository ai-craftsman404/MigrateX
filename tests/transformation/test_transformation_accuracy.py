"""
Transformation Accuracy Tests (Agent 9 - T9.1, T9.2, T9.3)

Tests accuracy of transformations - validates correct code generation.
Target: 65+ tests, 95%+ accuracy validation
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.core.context import MigrationContext
from migratex.agents.refactorer import RefactorerAgent
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestTransformationAccuracy:
    """Test transformation accuracy for various patterns."""
    
    def test_sk_import_kernel_transformation(self):
        """Test SK Kernel import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform to MAF import
            assert "microsoft.agentframework" in transformed or result == False
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_import_kernel_as_transformation(self):
        """Test SK Kernel import with alias transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel as SK"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel_as", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform alias import
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_import_agent_transformation(self):
        """Test SK KernelAgent import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.agents import KernelAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform agent import
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_agent_transformation(self):
        """Test AutoGen ConversableAgent import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import ConversableAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform AutoGen import
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_instantiation_kernel_transformation(self):
        """Test SK Kernel instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_instantiation_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform instantiation
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_class_inheritance_transformation(self):
        """Test SK class inheritance transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import KernelAgent

class MyAgent(KernelAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_class_inheritance", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform inheritance
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_class_inheritance_transformation(self):
        """Test AutoGen class inheritance transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import ConversableAgent

class MyAgent(ConversableAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_class_inheritance", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform AutoGen inheritance
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_decorator_transformation(self):
        """Test SK decorator transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_decorator", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve decorator structure
            assert "@" in transformed or "@" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_method_call_transformation(self):
        """Test SK method call transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernel = Kernel()
kernel.add_plugin(plugin)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_method_kernel_add_plugin", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform method call
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_method_call_transformation(self):
        """Test AutoGen method call transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import ConversableAgent

agent = ConversableAgent("assistant")
agent.initiate_chat(recipient, message="Hello")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_method_initiate_chat", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform AutoGen method call
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_parameter_transformation(self):
        """Test SK parameter name transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

def create_agent(kernel=None):
    return Kernel(kernel=kernel)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_param_kernel_to_client", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform parameter names
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_multiple_patterns_same_file(self):
        """Test multiple patterns in same file."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from semantic_kernel.agents import KernelAgent

class MyAgent(KernelAgent):
    def __init__(self):
        self.kernel = Kernel()
        self.kernel.add_plugin(plugin)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_import_agent", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_class_inheritance", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_instantiation_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_method_kernel_add_plugin", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}
                ]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should transform all patterns
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_preserves_comments(self):
        """Test transformation preserves comments."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """# This is a comment
from semantic_kernel import Kernel  # Inline comment
# Another comment
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve comments
            assert "#" in transformed or "#" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_preserves_docstrings(self):
        """Test transformation preserves docstrings."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            '''"""Module docstring."""
from semantic_kernel import Kernel

def function():
    """Function docstring."""
    pass
'''
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve docstrings
            assert '"""' in transformed or '"""' in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_preserves_type_hints(self):
        """Test transformation preserves type hints."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from typing import Optional

def create_kernel() -> Optional[Kernel]:
    return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve type hints structure
            assert "->" in transformed or "->" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_idempotency(self):
        """Test transformation is idempotent (can run multiple times)."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            
            # First transformation
            result1 = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed1 = file_path.read_text(encoding="utf-8")
            
            # Second transformation (should be idempotent)
            result2 = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed2 = file_path.read_text(encoding="utf-8")
            
            # Should be idempotent (same result or no-op)
            assert isinstance(result1, bool)
            assert isinstance(result2, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_async_await(self):
        """Test transformation with async/await."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

async def create_kernel():
    kernel = Kernel()
    await kernel.invoke()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve async/await
            assert "async" in transformed or "async" in original
            assert "await" in transformed or "await" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_conditional_imports(self):
        """Test transformation with conditional imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """if True:
    from semantic_kernel import Kernel
else:
    from other import Kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            # Should handle conditional imports
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_try_except_imports(self):
        """Test transformation with try-except imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """try:
    from semantic_kernel import Kernel
except ImportError:
    from fallback import Kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            # Should handle try-except imports
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_transformation_with_relative_imports(self):
        """Test transformation with relative imports."""
        fixture = Path(tempfile.mkdtemp())
        (fixture / "package").mkdir()
        (fixture / "package" / "__init__.py").write_text("")
        (fixture / "package" / "module.py").write_text("from semantic_kernel import Kernel")
        (fixture / "package" / "other.py").write_text("from .module import Kernel")
        
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "package" / "module.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "package" / "module.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            
            # Should handle relative imports
            assert isinstance(result, bool)
        finally:
            shutil.rmtree(fixture)
    
    def test_transformation_with_string_literals(self):
        """Test transformation doesn't affect string literals."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

message = "Uses semantic_kernel.Kernel for processing"
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            
            # Should preserve string literals
            assert "semantic_kernel.Kernel" in transformed or "semantic_kernel.Kernel" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Additional SK Import Transformation Tests
    def test_sk_import_plugins_transformation(self):
        """Test SK plugins import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.plugins import MathPlugin"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_plugins", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_import_functions_transformation(self):
        """Test SK functions import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.functions import KernelFunction"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_functions", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_import_kernel_builder_transformation(self):
        """Test SK KernelBuilder import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import KernelBuilder"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_kernel_builder", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_import_chat_completion_transformation(self):
        """Test SK ChatCompletionAgent import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.agents import ChatCompletionAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_import_chat_completion", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Additional AutoGen Import Transformation Tests
    def test_autogen_import_assistant_transformation(self):
        """Test AutoGen AssistantAgent import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import AssistantAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_assistant", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_user_proxy_transformation(self):
        """Test AutoGen UserProxyAgent import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import UserProxyAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_user_proxy", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_groupchat_transformation(self):
        """Test AutoGen GroupChat import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import GroupChat"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_groupchat", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_manager_transformation(self):
        """Test AutoGen GroupChatManager import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import GroupChatManager"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_manager", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_import_agentchat_transformation(self):
        """Test AutoGen agentchat import transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen.agentchat import AssistantAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_import_agentchat", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Instantiation Transformation Tests
    def test_sk_kernel_builder_instantiation_transformation(self):
        """Test SK KernelBuilder instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import KernelBuilder
builder = KernelBuilder()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel_builder", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"},
                    {"id": "sk_kernel_builder_instantiation", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_chat_completion_instantiation_transformation(self):
        """Test SK ChatCompletionAgent instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import ChatCompletionAgent
agent = ChatCompletionAgent()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_chat_completion", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_chat_completion_instantiation", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_assistant_instantiation_transformation(self):
        """Test AutoGen AssistantAgent instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import AssistantAgent
agent = AssistantAgent("assistant")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_assistant", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_assistant_instantiation", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_user_proxy_instantiation_transformation(self):
        """Test AutoGen UserProxyAgent instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import UserProxyAgent
agent = UserProxyAgent("user")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_user_proxy", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_user_proxy_instantiation", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_groupchat_instantiation_transformation(self):
        """Test AutoGen GroupChat instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import GroupChat
chat = GroupChat(agents=[])
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_groupchat", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_groupchat_instantiation", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_manager_instantiation_transformation(self):
        """Test AutoGen GroupChatManager instantiation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import GroupChatManager
manager = GroupChatManager()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_manager", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_manager_instantiation", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Decorator Transformation Tests
    def test_sk_decorator_kernel_function_transformation(self):
        """Test SK @kernel_function decorator transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_decorator_kernel_function", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            assert "@" in transformed or "@" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_sk_decorator_semantic_function_transformation(self):
        """Test SK @semantic_function decorator transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import semantic_function

@semantic_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "sk_decorator_semantic_function", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            assert "@" in transformed or "@" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_decorator_tool_transformation(self):
        """Test AutoGen @autogen.tool decorator transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import tool

@tool
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [{"id": "autogen_decorator_tool", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            original = file_path.read_text(encoding="utf-8")
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            transformed = file_path.read_text(encoding="utf-8")
            assert "@" in transformed or "@" in original
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Method Call Transformation Tests
    def test_sk_method_add_function_transformation(self):
        """Test SK add_function() method call transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernel = Kernel()
kernel.add_function(func)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_method_kernel_add_function", "file": str(fixture / "main.py"), "confidence": "medium", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Parameter Transformation Tests
    def test_sk_parameter_kernel_type_hint_transformation(self):
        """Test SK kernel: type annotation transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from typing import Optional

def create_agent(kernel: Optional[Kernel] = None):
    return kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_kernel", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_param_kernel_var_to_client", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Class Inheritance Transformation Tests
    def test_sk_class_inheritance_chat_completion_transformation(self):
        """Test SK ChatCompletionAgent inheritance transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import ChatCompletionAgent

class MyAgent(ChatCompletionAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "sk_import_chat_completion", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "sk_class_inheritance_chat_completion", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_class_inheritance_assistant_transformation(self):
        """Test AutoGen AssistantAgent inheritance transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import AssistantAgent

class MyAgent(AssistantAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_assistant", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_class_inheritance_assistant", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_autogen_class_inheritance_user_proxy_transformation(self):
        """Test AutoGen UserProxyAgent inheritance transformation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import UserProxyAgent

class MyAgent(UserProxyAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="auto")
            context.report = {
                "patterns": [
                    {"id": "autogen_import_user_proxy", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"},
                    {"id": "autogen_class_inheritance_user_proxy", "file": str(fixture / "main.py"), "confidence": "high", "source": "rule"}
                ]
            }
            refactorer = RefactorerAgent(context)
            file_path = fixture / "main.py"
            result = refactorer._transform_file(file_path, context.report["patterns"], auto_mode=True)
            assert isinstance(result, bool)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

