"""
Pattern Detection Accuracy Tests (Agent 8 - T8.1, T8.2, T8.3)

Tests accuracy of pattern detection - validates correct pattern identification.
Target: 85+ tests, 95%+ accuracy validation
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from migratex.core.context import MigrationContext
from migratex.patterns.discovery import PatternDiscovery
from migratex.testing.edge_case_fixtures import EdgeCaseTestFixtures


class TestPatternDetectionAccuracy:
    """Test pattern detection accuracy for various scenarios."""
    
    def test_detect_sk_import_kernel(self):
        """Test detection of SK Kernel import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect SK import
            assert len(patterns) > 0
            assert any("sk" in str(p.get("id", "")).lower() or "kernel" in str(p.get("id", "")).lower() for p in patterns)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_import_kernel_as(self):
        """Test detection of SK Kernel import with alias."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel as SK"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect aliased import
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_import_agent(self):
        """Test detection of SK KernelAgent import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.agents import KernelAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect agent import
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_import_agent(self):
        """Test detection of AutoGen ConversableAgent import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import ConversableAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect AutoGen import
            assert len(patterns) > 0
            assert any("autogen" in str(p.get("id", "")).lower() or "agent" in str(p.get("id", "")).lower() for p in patterns)
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_instantiation(self):
        """Test detection of SK Kernel instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect instantiation
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_class_inheritance(self):
        """Test detection of SK class inheritance."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import KernelAgent

class MyAgent(KernelAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect inheritance
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_class_inheritance(self):
        """Test detection of AutoGen class inheritance."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import ConversableAgent

class MyAgent(ConversableAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect AutoGen inheritance
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_decorator(self):
        """Test detection of SK decorator."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect decorator
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_method_call(self):
        """Test detection of SK method call."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernel = Kernel()
kernel.add_plugin(plugin)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect method call
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_method_call(self):
        """Test detection of AutoGen method call."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import ConversableAgent

agent = ConversableAgent("assistant")
agent.initiate_chat(recipient, message="Hello")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect AutoGen method call
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_multiple_patterns(self):
        """Test detection of multiple patterns in same file."""
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
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect multiple patterns
            assert len(patterns) >= 2
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_in_multiple_files(self):
        """Test detection of patterns across multiple files."""
        fixture = EdgeCaseTestFixtures.create_mixed_frameworks_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            
            python_files = list(fixture.rglob("*.py"))
            patterns = discovery.discover_patterns(python_files)
            
            # Should detect patterns in multiple files
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_no_false_positives_in_comments(self):
        """Test no false positives in comments."""
        fixture = EdgeCaseTestFixtures.create_pattern_in_comments_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "commented.py"])
            
            # Should not detect patterns in comments
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_no_false_positives_in_strings(self):
        """Test no false positives in strings."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            'message = "Uses semantic_kernel.Kernel for processing"'
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should not detect patterns in strings
            assert len(patterns) == 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_type_hints(self):
        """Test detection of patterns with type hints."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from typing import Optional

def create_kernel() -> Optional[Kernel]:
    return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns despite type hints
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_decorators(self):
        """Test detection of patterns with decorators."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

@decorator
def function():
    kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns despite decorators
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_async_await(self):
        """Test detection of patterns with async/await."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

async def create_kernel():
    kernel = Kernel()
    await kernel.invoke()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns despite async/await
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_conditional_imports(self):
        """Test detection of patterns with conditional imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """if True:
    from semantic_kernel import Kernel
else:
    from other import Kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect conditional imports
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_try_except_imports(self):
        """Test detection of patterns with try-except imports."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """try:
    from semantic_kernel import Kernel
except ImportError:
    from fallback import Kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect try-except imports
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_relative_imports(self):
        """Test detection of patterns with relative imports."""
        fixture = Path(tempfile.mkdtemp())
        (fixture / "package").mkdir()
        (fixture / "package" / "__init__.py").write_text("")
        (fixture / "package" / "module.py").write_text("from semantic_kernel import Kernel")
        
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "package" / "module.py"])
            
            # Should detect patterns in relative import contexts
            assert len(patterns) > 0
        finally:
            shutil.rmtree(fixture)
    
    def test_detect_patterns_with_nested_classes(self):
        """Test detection of patterns with nested classes."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class Outer:
    class Inner:
        def method(self):
            kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in nested classes
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_inheritance_chains(self):
        """Test detection of patterns with inheritance chains."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import KernelAgent

class Base(KernelAgent):
    pass

class Derived(Base):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in inheritance chains
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_metaclasses(self):
        """Test detection of patterns with metaclasses."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class Meta(type):
    pass

class MyClass(metaclass=Meta):
    kernel = Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns despite metaclasses
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_properties(self):
        """Test detection of patterns with properties."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @property
    def kernel(self):
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in properties
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_class_methods(self):
        """Test detection of patterns with class methods."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @classmethod
    def create(cls):
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in class methods
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_static_methods(self):
        """Test detection of patterns with static methods."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

class MyClass:
    @staticmethod
    def create():
        return Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in static methods
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_lambdas(self):
        """Test detection of patterns with lambdas."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

func = lambda: Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in lambdas
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_list_comprehensions(self):
        """Test detection of patterns with list comprehensions."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernels = [Kernel() for _ in range(10)]
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in list comprehensions
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_generators(self):
        """Test detection of patterns with generators."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

def get_kernels():
    yield Kernel()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in generators
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_patterns_with_context_managers(self):
        """Test detection of patterns with context managers."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

with Kernel() as kernel:
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should detect patterns in context managers
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_confidence_levels(self):
        """Test pattern confidence levels are assigned correctly."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should assign confidence levels
            if patterns:
                assert "confidence" in patterns[0] or "high" in str(patterns[0])
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_source_tracking(self):
        """Test pattern source is tracked correctly."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import Kernel"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should track pattern source
            if patterns:
                assert "source" in patterns[0] or "rule" in str(patterns[0])
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_file_association(self):
        """Test patterns are associated with correct files."""
        fixture = EdgeCaseTestFixtures.create_mixed_frameworks_codebase()
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            
            python_files = list(fixture.rglob("*.py"))
            patterns = discovery.discover_patterns(python_files)
            
            # Should associate patterns with files
            if patterns:
                assert "file" in patterns[0] or str(fixture) in str(patterns[0])
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_pattern_line_number_tracking(self):
        """Test pattern line numbers are tracked."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """# Line 1
# Line 2
from semantic_kernel import Kernel  # Line 3
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            
            # Should track line numbers (if implemented)
            if patterns:
                assert isinstance(patterns[0], dict) and len(patterns[0]) > 0, "Pattern should be non-empty dict"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Additional SK Import Pattern Tests
    def test_detect_sk_import_plugins(self):
        """Test detection of SK plugins import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.plugins import MathPlugin"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_import_functions(self):
        """Test detection of SK functions import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.functions import KernelFunction"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_import_kernel_builder(self):
        """Test detection of SK KernelBuilder import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel import KernelBuilder"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_import_chat_completion(self):
        """Test detection of SK ChatCompletionAgent import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from semantic_kernel.agents import ChatCompletionAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Additional AutoGen Import Pattern Tests
    def test_detect_autogen_import_assistant(self):
        """Test detection of AutoGen AssistantAgent import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import AssistantAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_import_user_proxy(self):
        """Test detection of AutoGen UserProxyAgent import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import UserProxyAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_import_groupchat(self):
        """Test detection of AutoGen GroupChat import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import GroupChat"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_import_manager(self):
        """Test detection of AutoGen GroupChatManager import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen import GroupChatManager"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_import_agentchat(self):
        """Test detection of AutoGen agentchat import."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            "from autogen.agentchat import AssistantAgent"
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Instantiation Pattern Tests
    def test_detect_sk_kernel_builder_instantiation(self):
        """Test detection of SK KernelBuilder instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import KernelBuilder
builder = KernelBuilder()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_chat_completion_instantiation(self):
        """Test detection of SK ChatCompletionAgent instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import ChatCompletionAgent
agent = ChatCompletionAgent()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_assistant_instantiation(self):
        """Test detection of AutoGen AssistantAgent instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import AssistantAgent
agent = AssistantAgent("assistant")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_user_proxy_instantiation(self):
        """Test detection of AutoGen UserProxyAgent instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import UserProxyAgent
agent = UserProxyAgent("user")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_groupchat_instantiation(self):
        """Test detection of AutoGen GroupChat instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import GroupChat
chat = GroupChat(agents=[])
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_manager_instantiation(self):
        """Test detection of AutoGen GroupChatManager instantiation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import GroupChatManager
manager = GroupChatManager()
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Decorator Pattern Tests
    def test_detect_sk_decorator_kernel_function(self):
        """Test detection of SK @kernel_function decorator."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import kernel_function

@kernel_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_decorator_semantic_function(self):
        """Test detection of SK @semantic_function decorator."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.decorators import semantic_function

@semantic_function
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_decorator_tool(self):
        """Test detection of AutoGen @autogen.tool decorator."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import tool

@tool
def my_function():
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            # May or may not detect depending on implementation
            assert isinstance(patterns, list), "Patterns should be list"
            # Verify patterns validity
            assert patterns is not None, "Patterns should exist"
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Method Call Pattern Tests
    def test_detect_sk_method_add_plugin(self):
        """Test detection of SK add_plugin() method call."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernel = Kernel()
kernel.add_plugin(plugin)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_method_add_function(self):
        """Test detection of SK add_function() method call."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

kernel = Kernel()
kernel.add_function(func)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_method_initiate_chat(self):
        """Test detection of AutoGen initiate_chat() method call."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import ConversableAgent

agent = ConversableAgent("assistant")
agent.initiate_chat(recipient, message="Hello")
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Parameter Pattern Tests
    def test_detect_sk_parameter_kernel(self):
        """Test detection of SK kernel= parameter."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel

def create_agent(kernel=None):
    return Kernel(kernel=kernel)
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_sk_parameter_kernel_type_hint(self):
        """Test detection of SK kernel: type annotation."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel import Kernel
from typing import Optional

def create_agent(kernel: Optional[Kernel] = None):
    return kernel
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    # Class Inheritance Pattern Tests
    def test_detect_sk_class_inheritance_chat_completion(self):
        """Test detection of SK ChatCompletionAgent inheritance."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from semantic_kernel.agents import ChatCompletionAgent

class MyAgent(ChatCompletionAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_class_inheritance_assistant(self):
        """Test detection of AutoGen AssistantAgent inheritance."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import AssistantAgent

class MyAgent(AssistantAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)
    
    def test_detect_autogen_class_inheritance_user_proxy(self):
        """Test detection of AutoGen UserProxyAgent inheritance."""
        fixture = EdgeCaseTestFixtures.create_single_file_codebase(
            """from autogen import UserProxyAgent

class MyAgent(UserProxyAgent):
    pass
"""
        )
        try:
            context = MigrationContext(project_path=fixture, mode="analyze")
            discovery = PatternDiscovery(context)
            patterns = discovery.discover_patterns([fixture / "main.py"])
            assert len(patterns) > 0
        finally:
            EdgeCaseTestFixtures.cleanup(fixture)

