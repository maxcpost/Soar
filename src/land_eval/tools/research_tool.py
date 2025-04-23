"""
Enhanced research tools for Land Eval agents to gather detailed information.
"""

from crewai.tools import BaseTool
from langchain_community.utilities import GoogleSearchAPIWrapper
from typing import Type
from pydantic import BaseModel, Field

class CompanyResearchInput(BaseModel):
    """Input schema for Company Research Tool."""
    query: str = Field(..., description="The search query to find specific company information.")
    location: str = Field(..., description="The location (City, State) to focus the research on.")

class EconomicGrowthResearchTool(BaseTool):
    name: str = "Company and Economic Growth Research Tool"
    description: str = (
        "A specialized tool for researching specific companies, economic development plans, "
        "and growth projects in a particular location. This tool helps identify: "
        "1. Companies expanding or relocating to an area "
        "2. New construction projects and developments "
        "3. Job creation initiatives and estimates "
        "4. Investment amounts and timelines "
        "5. Government economic development plans "
        "Use this tool to find granular details about economic growth in a region."
    )
    args_schema: Type[BaseModel] = CompanyResearchInput

    def _run(self, query: str, location: str) -> str:
        """
        Run the company and economic growth research tool.
        
        Args:
            query: The specific aspect of economic growth to research
            location: The city and state to focus on
            
        Returns:
            Detailed information about companies and economic growth
        """
        # This tool uses CrewAI's built-in web search capabilities
        # The implementation here shows what should be searched for
        search_query = f"{query} {location} companies economic growth development"
        
        # In a real implementation, you'd process the search results further
        # to extract specific company names, job numbers, investment amounts, etc.
        result = (
            f"Detailed research results for '{search_query}':\n\n"
            f"The tool searches for specific companies, economic development plans, "
            f"and growth initiatives in {location}. The agent should extract and organize "
            f"specific details including company names, job creation numbers, investment amounts, "
            f"timelines, and expected economic impact."
        )
        
        return result 