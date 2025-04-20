"""
Tools package for Land Eval.

This package is reserved for custom tools that can be used by the crew's agents.
The directory is kept for future extension and tool development.
All agents have access to built-in web search capabilities for detailed research.
"""

from src.land_eval.tools.research_tool import EconomicGrowthResearchTool

__all__ = [
    "EconomicGrowthResearchTool",
]
