"""
Agent base classes and framework
"""

from abc import ABC, abstractmethod
from migratex.core.context import MigrationContext


class BaseAgent(ABC):
    """
    Base class for all migration agents.
    All agents receive MigrationContext and operate through it.
    """
    
    def __init__(self, context: MigrationContext):
        self.context = context
    
    @abstractmethod
    def run(self):
        """Execute the agent's main logic."""
        pass

