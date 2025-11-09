"""
Pattern loader module - Load only relevant patterns
"""

from typing import List
from migratex.patterns.library import PatternLibrary


class PatternLoader:
    """
    Loads only relevant patterns based on discovery results.
    """
    
    def __init__(self, library: PatternLibrary):
        self.library = library
    
    def load_relevant(self, detected_pattern_ids: List[str]):
        """
        Load only patterns that were detected in the codebase.
        """
        # Filter library to only include detected patterns
        relevant_patterns = {}
        for pattern_id in detected_pattern_ids:
            pattern = self.library.get_pattern(pattern_id)
            if pattern:
                relevant_patterns[pattern_id] = pattern
        
        return relevant_patterns

