"""
Python-specific pattern mappings for SK/AutoGen → MAF transformations.
"""

from typing import Dict, Any


class PythonPatterns:
    """
    Python-specific SK→MAF pattern mappings.
    Contains detailed pattern definitions for Python code transformations.
    Patterns are organised by category: imports, instantiations, decorators, 
    class inheritance, method calls, and configuration.
    """
    
    @staticmethod
    def get_patterns() -> Dict[str, Dict[str, Any]]:
        """Get comprehensive Python-specific pattern definitions."""
        patterns = {
            # ========== Semantic Kernel Import Patterns ==========
            "sk_import_kernel": {
                "id": "SK_IMPORT_KERNEL",
                "pattern": r"from semantic_kernel import Kernel",
                "replacement": "from microsoft.agentframework import AgentFrameworkClient",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace Kernel import with AgentFrameworkClient"
            },
            "sk_import_kernel_as": {
                "id": "SK_IMPORT_KERNEL_AS",
                "pattern": r"from semantic_kernel import Kernel as \w+",
                "replacement": "from microsoft.agentframework import AgentFrameworkClient",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace Kernel import (with alias) with AgentFrameworkClient"
            },
            "sk_import_agent": {
                "id": "SK_IMPORT_AGENT",
                "pattern": r"from semantic_kernel\.agents import KernelAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace KernelAgent import with Agent"
            },
            "sk_import_chat_completion": {
                "id": "SK_IMPORT_CHAT_COMPLETION",
                "pattern": r"from semantic_kernel\.agents import ChatCompletionAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace ChatCompletionAgent import with Agent"
            },
            "sk_import_plugins": {
                "id": "SK_IMPORT_PLUGINS",
                "pattern": r"from semantic_kernel\.plugins import",
                "replacement": "from microsoft.agentframework.tools import",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace plugins imports with tools imports"
            },
            "sk_import_functions": {
                "id": "SK_IMPORT_FUNCTIONS",
                "pattern": r"from semantic_kernel\.functions import",
                "replacement": "from microsoft.agentframework.tools import",
                "confidence": "high",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace functions imports with tools imports"
            },
            "sk_import_kernel_builder": {
                "id": "SK_IMPORT_KERNEL_BUILDER",
                "pattern": r"from semantic_kernel import KernelBuilder",
                "replacement": "from microsoft.agentframework import AgentFrameworkClientBuilder",
                "confidence": "medium",
                "type": "import",
                "framework": "semantic_kernel",
                "description": "Replace KernelBuilder import with AgentFrameworkClientBuilder"
            },
            
            # ========== AutoGen Import Patterns ==========
            "autogen_import_conversable": {
                "id": "AUTOGEN_IMPORT_CONVERSABLE",
                "pattern": r"from autogen import ConversableAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace ConversableAgent import with Agent"
            },
            "autogen_import_assistant": {
                "id": "AUTOGEN_IMPORT_ASSISTANT",
                "pattern": r"from autogen import AssistantAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace AssistantAgent import with Agent"
            },
            "autogen_import_user_proxy": {
                "id": "AUTOGEN_IMPORT_USER_PROXY",
                "pattern": r"from autogen import UserProxyAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace UserProxyAgent import with Agent"
            },
            "autogen_import_groupchat": {
                "id": "AUTOGEN_IMPORT_GROUPCHAT",
                "pattern": r"from autogen import GroupChat",
                "replacement": "from microsoft.agentframework.orchestration import WorkflowGraph",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace GroupChat import with WorkflowGraph"
            },
            "autogen_import_manager": {
                "id": "AUTOGEN_IMPORT_MANAGER",
                "pattern": r"from autogen import GroupChatManager",
                "replacement": "from microsoft.agentframework.orchestration import WorkflowOrchestrator",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace GroupChatManager import with WorkflowOrchestrator"
            },
            "autogen_import_agentchat": {
                "id": "AUTOGEN_IMPORT_AGENTCHAT",
                "pattern": r"from autogen\.agentchat import",
                "replacement": "from microsoft.agentframework.orchestration import",
                "confidence": "high",
                "type": "import",
                "framework": "autogen",
                "description": "Replace agentchat imports with orchestration imports"
            },
            
            # ========== Instantiation Patterns ==========
            "sk_kernel_instantiation": {
                "id": "SK_KERNEL_INSTANTIATION",
                "pattern": r"Kernel\(",
                "replacement": "AgentFrameworkClient(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "semantic_kernel",
                "description": "Replace Kernel() instantiation with AgentFrameworkClient()"
            },
            "sk_kernel_builder_instantiation": {
                "id": "SK_KERNEL_BUILDER_INSTANTIATION",
                "pattern": r"KernelBuilder\(",
                "replacement": "AgentFrameworkClientBuilder(",
                "confidence": "medium",
                "type": "instantiation",
                "framework": "semantic_kernel",
                "description": "Replace KernelBuilder() instantiation with AgentFrameworkClientBuilder()"
            },
            "sk_agent_instantiation": {
                "id": "SK_AGENT_INSTANTIATION",
                "pattern": r"KernelAgent\(",
                "replacement": "Agent(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "semantic_kernel",
                "description": "Replace KernelAgent() instantiation with Agent()"
            },
            "sk_chat_completion_instantiation": {
                "id": "SK_CHAT_COMPLETION_INSTANTIATION",
                "pattern": r"ChatCompletionAgent\(",
                "replacement": "Agent(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "semantic_kernel",
                "description": "Replace ChatCompletionAgent() instantiation with Agent()"
            },
            "autogen_conversable_instantiation": {
                "id": "AUTOGEN_CONVERSABLE_INSTANTIATION",
                "pattern": r"ConversableAgent\(",
                "replacement": "Agent(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "autogen",
                "description": "Replace ConversableAgent() instantiation with Agent()"
            },
            "autogen_assistant_instantiation": {
                "id": "AUTOGEN_ASSISTANT_INSTANTIATION",
                "pattern": r"AssistantAgent\(",
                "replacement": "Agent(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "autogen",
                "description": "Replace AssistantAgent() instantiation with Agent()"
            },
            "autogen_user_proxy_instantiation": {
                "id": "AUTOGEN_USER_PROXY_INSTANTIATION",
                "pattern": r"UserProxyAgent\(",
                "replacement": "Agent(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "autogen",
                "description": "Replace UserProxyAgent() instantiation with Agent()"
            },
            "autogen_groupchat_instantiation": {
                "id": "AUTOGEN_GROUPCHAT_INSTANTIATION",
                "pattern": r"GroupChat\(",
                "replacement": "WorkflowGraph(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "autogen",
                "description": "Replace GroupChat() instantiation with WorkflowGraph()"
            },
            "autogen_manager_instantiation": {
                "id": "AUTOGEN_MANAGER_INSTANTIATION",
                "pattern": r"GroupChatManager\(",
                "replacement": "WorkflowOrchestrator(",
                "confidence": "high",
                "type": "instantiation",
                "framework": "autogen",
                "description": "Replace GroupChatManager() instantiation with WorkflowOrchestrator()"
            },
            
            # ========== Class Inheritance Patterns ==========
            "sk_class_inheritance_kernel_agent": {
                "id": "SK_CLASS_INHERITANCE_KERNEL_AGENT",
                "pattern": r"class \w+\(KernelAgent\)",
                "replacement": "class {name}(Agent)",
                "confidence": "high",
                "type": "class_inheritance",
                "framework": "semantic_kernel",
                "description": "Replace KernelAgent base class with Agent"
            },
            "sk_class_inheritance_chat_completion": {
                "id": "SK_CLASS_INHERITANCE_CHAT_COMPLETION",
                "pattern": r"class \w+\(ChatCompletionAgent\)",
                "replacement": "class {name}(Agent)",
                "confidence": "high",
                "type": "class_inheritance",
                "framework": "semantic_kernel",
                "description": "Replace ChatCompletionAgent base class with Agent"
            },
            "autogen_class_inheritance_conversable": {
                "id": "AUTOGEN_CLASS_INHERITANCE_CONVERSABLE",
                "pattern": r"class \w+\(ConversableAgent\)",
                "replacement": "class {name}(Agent)",
                "confidence": "high",
                "type": "class_inheritance",
                "framework": "autogen",
                "description": "Replace ConversableAgent base class with Agent"
            },
            "autogen_class_inheritance_assistant": {
                "id": "AUTOGEN_CLASS_INHERITANCE_ASSISTANT",
                "pattern": r"class \w+\(AssistantAgent\)",
                "replacement": "class {name}(Agent)",
                "confidence": "high",
                "type": "class_inheritance",
                "framework": "autogen",
                "description": "Replace AssistantAgent base class with Agent"
            },
            "autogen_class_inheritance_user_proxy": {
                "id": "AUTOGEN_CLASS_INHERITANCE_USER_PROXY",
                "pattern": r"class \w+\(UserProxyAgent\)",
                "replacement": "class {name}(Agent)",
                "confidence": "high",
                "type": "class_inheritance",
                "framework": "autogen",
                "description": "Replace UserProxyAgent base class with Agent"
            },
            
            # ========== Decorator Patterns ==========
            "sk_decorator_kernel_function": {
                "id": "SK_DECORATOR_KERNEL_FUNCTION",
                "pattern": r"@kernel_function",
                "replacement": "@tool",
                "confidence": "high",
                "type": "decorator",
                "framework": "semantic_kernel",
                "description": "Replace @kernel_function decorator with @tool"
            },
            "sk_decorator_semantic_function": {
                "id": "SK_DECORATOR_SEMANTIC_FUNCTION",
                "pattern": r"@semantic_function",
                "replacement": "@tool",
                "confidence": "high",
                "type": "decorator",
                "framework": "semantic_kernel",
                "description": "Replace @semantic_function decorator with @tool"
            },
            "autogen_decorator_tool": {
                "id": "AUTOGEN_DECORATOR_TOOL",
                "pattern": r"@autogen\.tool",
                "replacement": "@tool",
                "confidence": "high",
                "type": "decorator",
                "framework": "autogen",
                "description": "Replace @autogen.tool decorator with @tool"
            },
            
            # ========== Method Call Patterns ==========
            "sk_method_kernel_add_plugin": {
                "id": "SK_METHOD_KERNEL_ADD_PLUGIN",
                "pattern": r"\.add_plugin\(",
                "replacement": ".add_tool(",
                "confidence": "medium",
                "type": "method_call",
                "framework": "semantic_kernel",
                "description": "Replace add_plugin() method with add_tool()"
            },
            "sk_method_kernel_add_function": {
                "id": "SK_METHOD_KERNEL_ADD_FUNCTION",
                "pattern": r"\.add_function\(",
                "replacement": ".add_tool(",
                "confidence": "medium",
                "type": "method_call",
                "framework": "semantic_kernel",
                "description": "Replace add_function() method with add_tool()"
            },
            "autogen_method_initiate_chat": {
                "id": "AUTOGEN_METHOD_INITIATE_CHAT",
                "pattern": r"\.initiate_chat\(",
                "replacement": ".invoke(",
                "confidence": "medium",
                "type": "method_call",
                "framework": "autogen",
                "description": "Replace initiate_chat() method with invoke()"
            },
            
            # ========== Parameter Name Patterns ==========
            "sk_param_kernel_to_client": {
                "id": "SK_PARAM_KERNEL_TO_CLIENT",
                "pattern": r"kernel=",
                "replacement": "client=",
                "confidence": "high",
                "type": "parameter",
                "framework": "semantic_kernel",
                "description": "Replace kernel= parameter with client="
            },
            "sk_param_kernel_var_to_client": {
                "id": "SK_PARAM_KERNEL_VAR_TO_CLIENT",
                "pattern": r"kernel:",
                "replacement": "client:",
                "confidence": "high",
                "type": "parameter",
                "framework": "semantic_kernel",
                "description": "Replace kernel: type annotation with client:"
            }
        }
        
        return patterns

