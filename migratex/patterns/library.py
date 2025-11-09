"""
Pattern library module - SK→MAF pattern mappings
"""

from typing import Dict, List, Any, Optional
from migratex.docs import migration_docs


class PatternLibrary:
    """
    Manages the library of SK→MAF transformation patterns.
    Patterns have confidence levels and sources.
    Uses Microsoft's official migration guides as the source of truth.
    """
    
    def __init__(self):
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self._load_patterns_from_docs()
    
    def _load_patterns_from_docs(self):
        """Load patterns from migration documentation and PythonPatterns."""
        # Get official pattern mappings from documentation
        sk_mappings = migration_docs.get_pattern_mappings("semantic_kernel")
        autogen_mappings = migration_docs.get_pattern_mappings("autogen")
        
        # Load patterns from PythonPatterns (comprehensive pattern set)
        try:
            from migratex.languages.python.patterns import PythonPatterns
            python_patterns = PythonPatterns.get_patterns()
            
            # Convert PythonPatterns format to PatternLibrary format
            for pattern_key, pattern_def in python_patterns.items():
                pattern_id = pattern_def.get("id")
                if pattern_id:
                    # Get migration guide URL
                    framework = pattern_def.get("framework", "")
                    guide = migration_docs.get_migration_guide(framework) if framework else None
                    guide_url = guide.get("url") if guide else None
                    
                    self.patterns[pattern_id] = {
                        "id": pattern_id,
                        "confidence": pattern_def.get("confidence", "medium"),
                        "source": "rule",
                        "type": pattern_def.get("type", "unknown"),
                        "framework": framework,
                        "from": pattern_def.get("pattern", ""),
                        "to": pattern_def.get("replacement", ""),
                        "pattern": pattern_def.get("pattern", ""),  # Keep regex pattern
                        "replacement": pattern_def.get("replacement", ""),  # Keep replacement
                        "description": pattern_def.get("description", ""),
                        "migration_guide_url": guide_url
                    }
        except ImportError:
            # Fallback if PythonPatterns not available
            pass
        
        # Core Semantic Kernel patterns (fallback if PythonPatterns not loaded)
        if "SK_IMPORT_KERNEL" not in self.patterns:
            self.patterns["SK_IMPORT_KERNEL"] = {
                "id": "SK_IMPORT_KERNEL",
                "confidence": "high",
                "source": "rule",
                "type": "import",
                "framework": "semantic_kernel",
                "from": "from semantic_kernel import Kernel",
                "to": "from microsoft.agentframework import AgentFrameworkClient",
                "pattern": r"from semantic_kernel import Kernel",
                "replacement": "from microsoft.agentframework import AgentFrameworkClient",
                "description": "Replace Kernel import with AgentFrameworkClient",
                "migration_guide_url": migration_docs.get_migration_guide("semantic_kernel").get("url") if migration_docs.get_migration_guide("semantic_kernel") else None
            }
        
        # Core AutoGen patterns (fallback if PythonPatterns not loaded)
        if "AUTOGEN_IMPORT_CONVERSABLE" not in self.patterns:
            self.patterns["AUTOGEN_IMPORT_CONVERSABLE"] = {
                "id": "AUTOGEN_IMPORT_CONVERSABLE",
                "confidence": "high",
                "source": "rule",
                "type": "import",
                "framework": "autogen",
                "from": "from autogen import ConversableAgent",
                "to": "from microsoft.agentframework.agents import Agent",
                "pattern": r"from autogen import ConversableAgent",
                "replacement": "from microsoft.agentframework.agents import Agent",
                "description": "Replace ConversableAgent import with Agent",
                "migration_guide_url": migration_docs.get_migration_guide("autogen").get("url") if migration_docs.get_migration_guide("autogen") else None
            }
        
        # Load additional patterns from documentation if available
        # Note: sk_mappings structure may vary, so we check type before iterating
        imports_data = sk_mappings.get("imports")
        if imports_data:
            # Handle both dict and list formats
            if isinstance(imports_data, dict):
                # If it's a dict, convert to list format
                imports_list = [imports_data]
            elif isinstance(imports_data, list):
                imports_list = imports_data
            else:
                imports_list = []
            
            for imp_pattern in imports_list:
                # Handle both dict and string formats
                if isinstance(imp_pattern, dict):
                    pattern_id = f"SK_IMPORT_{imp_pattern.get('name', '').upper()}"
                    if pattern_id not in self.patterns:
                        self.patterns[pattern_id] = {
                            "id": pattern_id,
                            "confidence": "high",
                            "source": "rule",
                            "type": "import",
                            "framework": "semantic_kernel",
                            "from": imp_pattern.get("from", ""),
                            "to": imp_pattern.get("to", ""),
                            "pattern": imp_pattern.get("from", ""),
                            "replacement": imp_pattern.get("to", ""),
                            "description": imp_pattern.get("notes", ""),
                            "migration_guide_url": migration_docs.get_migration_guide("semantic_kernel").get("url") if migration_docs.get_migration_guide("semantic_kernel") else None
                        }
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific pattern by ID."""
        return self.patterns.get(pattern_id)
    
    def get_all_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all patterns."""
        return self.patterns
    
    def load_relevant(self, pattern_ids: List[str]):
        """Load only relevant patterns based on discovery."""
        # Filter patterns to only those detected in codebase
        relevant_patterns = {}
        for pattern_id in pattern_ids:
            if pattern_id in self.patterns:
                relevant_patterns[pattern_id] = self.patterns[pattern_id]
        
        # Store filtered patterns (can be used for optimization)
        self.relevant_patterns = relevant_patterns
        return relevant_patterns
    
    def is_high_confidence(self, pattern_id: str) -> bool:
        """Check if pattern is high confidence (rule-based)."""
        pattern = self.get_pattern(pattern_id)
        if pattern:
            return (
                pattern.get("confidence") == "high" and
                pattern.get("source") == "rule"
            )
        return False

