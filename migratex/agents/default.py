"""
Default/Coordinator Agent
"""

from migratex.agents import BaseAgent


class DefaultAgent(BaseAgent):
    """
    Coordinator agent for all work in the repo.
    Understands the goal and coordinates sub-tasks.
    """
    
    def run(self):
        """Coordinate migration workflow."""
        # This agent coordinates the overall workflow
        # Currently handled by Orchestrator, but kept for consistency with AGENTS.md
        pass

