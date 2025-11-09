"""
Python language support - Pattern detector
"""

from pathlib import Path
from typing import List, Dict, Any
import ast


class PythonDetector:
    """
    Detects SK/AutoGen patterns in Python code.
    Uses ast module for fast analysis.
    """
    
    def detect_patterns(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Detect patterns in a Python file.
        Returns list of detected patterns with metadata.
        """
        detected_patterns = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=str(file_path))
            
            # Detect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if self._is_sk_autogen_module(module):
                        pattern = {
                            "id": f"IMPORT_{module.upper().replace('.', '_')}",
                            "type": "import",
                            "module": module,
                            "confidence": "high",
                            "source": "rule",
                            "line": node.lineno,
                            "lineno": node.lineno,
                        }
                        detected_patterns.append(pattern)
                
                elif isinstance(node, ast.ClassDef):
                    # Detect base classes
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            base_name = base.id
                            if self._is_sk_autogen_class(base_name):
                                pattern = {
                                    "id": f"CLASS_{base_name}",
                                    "type": "class_inheritance",
                                    "class": base_name,
                                    "confidence": "high",
                                    "source": "rule",
                                    "line": node.lineno,
                                    "lineno": node.lineno,
                                }
                                detected_patterns.append(pattern)
        
        except Exception as e:
            # If parsing fails, skip this file
            pass
        
        return detected_patterns
    
    def _is_sk_autogen_module(self, module: str) -> bool:
        """Check if module is SK or AutoGen."""
        sk_modules = ["semantic_kernel", "sk"]
        autogen_modules = ["autogen", "autogen.agentchat", "autogen.ext"]
        
        return (
            any(module.startswith(m) for m in sk_modules) or
            any(module.startswith(m) for m in autogen_modules)
        )
    
    def _is_sk_autogen_class(self, class_name: str) -> bool:
        """Check if class name suggests SK or AutoGen."""
        sk_classes = ["Kernel", "KernelFunction", "SemanticFunction", "KernelAgent"]
        autogen_classes = ["ConversableAgent", "AssistantAgent", "UserProxyAgent", "GroupChat"]
        
        return class_name in sk_classes or class_name in autogen_classes

