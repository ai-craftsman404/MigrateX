"""
Documentation resources for migration agents.

This module provides access to Microsoft's official migration guides,
pattern mappings, and best practices for all specialized agents.
"""

from pathlib import Path
from typing import Dict, List, Optional


class MigrationDocumentation:
    """
    Centralized documentation resource for migration agents.
    Provides access to Microsoft's official migration guides and patterns.
    """
    
    def __init__(self):
        self.docs_dir = Path(__file__).parent
        self._load_documentation()
    
    def _load_documentation(self):
        """Load documentation resources."""
        self.guides = {
            "semantic_kernel": {
                "url": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/",
                "samples_url": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/samples",
                "title": "Semantic Kernel to Microsoft Agent Framework Migration Guide"
            },
            "autogen": {
                "url": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/",
                "title": "AutoGen to Microsoft Agent Framework Migration Guide"
            }
        }
    
    def get_migration_guide(self, framework: str) -> Optional[Dict]:
        """Get migration guide for a specific framework."""
        return self.guides.get(framework)
    
    def get_pattern_mappings(self, framework: str) -> Dict:
        """Get pattern mappings for a framework."""
        if framework == "semantic_kernel":
            return self._get_sk_pattern_mappings()
        elif framework == "autogen":
            return self._get_autogen_pattern_mappings()
        return {}
    
    def _get_sk_pattern_mappings(self) -> Dict:
        """Semantic Kernel to MAF pattern mappings."""
        return {
            "imports": {
                "from": "semantic_kernel",
                "to": "microsoft.agentframework",
                "notes": "Package imports change from semantic_kernel to microsoft.agentframework"
            },
            "agent_types": {
                "from": "KernelAgent, ChatCompletionAgent",
                "to": "Agent (unified type)",
                "notes": "Agent types consolidated into unified Agent class"
            },
            "dependency_injection": {
                "from": "IKernel, KernelBuilder",
                "to": "AgentFrameworkClient, dependency injection patterns",
                "notes": "Client initialization and DI patterns updated"
            }
        }
    
    def _get_autogen_pattern_mappings(self) -> Dict:
        """AutoGen to MAF pattern mappings."""
        return {
            "agent_types": {
                "from": "ConversableAgent, AssistantAgent, UserProxyAgent",
                "to": "Agent (unified type)",
                "notes": "AutoGen agent types unified into MAF Agent class"
            },
            "multi_agent": {
                "from": "GroupChat, GroupChatManager",
                "to": "Agent orchestration patterns",
                "notes": "Multi-agent patterns updated to MAF orchestration"
            },
            "tools": {
                "from": "@tool decorator, function calling",
                "to": "MAF tool integration patterns",
                "notes": "Tool integration patterns updated"
            }
        }
    
    def get_best_practices(self) -> List[str]:
        """Get migration best practices."""
        return [
            "Start with package import changes",
            "Update agent type declarations",
            "Review dependency injection patterns",
            "Test individual components before full migration",
            "Use official migration samples as reference",
            "Verify resource management patterns",
            "Check client initialization changes"
        ]
    
    def get_reference_urls(self) -> Dict[str, str]:
        """Get reference URLs for agents."""
        return {
            "sk_migration_guide": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/",
            "sk_samples": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel/samples",
            "autogen_migration_guide": "https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/",
            "maf_overview": "https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview",
            "maf_docs": "https://learn.microsoft.com/en-us/agent-framework/"
        }


# Global instance accessible to all agents
migration_docs = MigrationDocumentation()

