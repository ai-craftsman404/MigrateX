"""
Pattern discovery module - Detect patterns during analyze phase
"""

from typing import Dict, List, Any
from pathlib import Path


class PatternDiscovery:
    """
    Discovers SK/AutoGen patterns in codebase during analyze phase.
    """
    
    def __init__(self, context):
        self.context = context
    
    def discover_patterns(self, files: List[Path]) -> List[Dict[str, Any]]:
        """
        Discover patterns in the given files.
        Returns list of detected patterns with metadata.
        """
        detected_patterns = []
        
        # This will use the language-specific detector
        # For Python MVP, use Python detector
        from migratex.languages.python.detector import PythonDetector
        
        detector = PythonDetector()
        
        for file_path in files:
            if file_path.suffix == ".py":
                patterns = detector.detect_patterns(file_path)
                for pattern in patterns:
                    pattern["file"] = str(file_path)
                    detected_patterns.append(pattern)
        
        return detected_patterns

