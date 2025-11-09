"""
Pattern cache module - YAML-based pattern decision cache
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class PatternCache:
    """
    Manages pattern decision cache in YAML format.
    Stores user decisions and pattern metadata.
    """
    
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.cache_data: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Load cache from file if it exists."""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r") as f:
                    self.cache_data = yaml.safe_load(f) or {}
            except Exception:
                self.cache_data = {}
        
        if "patterns" not in self.cache_data:
            self.cache_data["patterns"] = {}
    
    def _save(self):
        """Save cache to file."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            yaml.dump(self.cache_data, f, default_flow_style=False)
    
    def exists(self) -> bool:
        """Check if cache file exists."""
        return self.cache_path.exists()
    
    def get_decision(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get decision for a pattern."""
        return self.cache_data["patterns"].get(pattern_id)
    
    def set_decision(
        self,
        pattern_id: str,
        decision: str,  # "auto_apply", "manual", "skip"
        notes: Optional[str] = None,
        min_confidence: Optional[str] = None
    ):
        """Set decision for a pattern."""
        if pattern_id not in self.cache_data["patterns"]:
            self.cache_data["patterns"][pattern_id] = {}
        
        self.cache_data["patterns"][pattern_id].update({
            "decision": decision,
            "lastUpdated": datetime.utcnow().isoformat() + "Z",
        })
        
        if notes:
            self.cache_data["patterns"][pattern_id]["notes"] = notes
        if min_confidence:
            self.cache_data["patterns"][pattern_id]["minConfidence"] = min_confidence
        
        self._save()
    
    def get_all_decisions(self) -> Dict[str, Dict[str, Any]]:
        """Get all cached decisions."""
        return self.cache_data.get("patterns", {})
    
    def clear(self):
        """Clear the cache."""
        self.cache_data = {"patterns": {}}
        self._save()
    
    def should_auto_apply(self, pattern_id: str) -> bool:
        """Check if pattern should be auto-applied based on cache."""
        decision = self.get_decision(pattern_id)
        if decision:
            return decision.get("decision") == "auto_apply"
        return False

