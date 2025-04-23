"""
Micro-market analysis tools for Land Eval agents to compare subject property to immediate neighborhood.
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class MicroMarketInput(BaseModel):
    """Input schema for Micro-Market Analysis Tool."""
    property_location: str = Field(..., description="The exact location of the subject property (address or coordinates).")
    radius: float = Field(default=1.0, description="Radius in miles to define the immediate neighborhood (default: 1 mile).")
    property_type: str = Field(default="", description="Optional property type for comparison (e.g., 'residential', 'commercial', 'mixed-use').")

class MicroMarketAnalysisTool(BaseTool):
    name: str = "Micro-Market Analysis Tool"
    description: str = (
        "A specialized tool for analyzing the immediate neighborhood surrounding a property "
        "and comparing it with the subject property. This tool helps identify: "
        "1. Property characteristics and values in the immediate vicinity "
        "2. Recent sales and listings within the defined radius "
        "3. Neighborhood amenities and points of interest "
        "4. Local infrastructure and accessibility "
        "5. Micro-level growth trends and development activity "
        "Use this tool to understand how the subject property compares to its immediate surroundings."
    )
    args_schema: Type[BaseModel] = MicroMarketInput

    def _run(self, property_location: str, radius: float = 1.0, property_type: str = "") -> str:
        """
        Run the micro-market analysis tool.
        
        Args:
            property_location: The exact location of the subject property
            radius: Radius in miles to define the immediate neighborhood
            property_type: Optional property type for comparison
            
        Returns:
            Detailed micro-market analysis comparing the subject property to its neighborhood
        """
        # Construct appropriate search query based on inputs
        search_query_base = f"{property_location} neighborhood property values development"
        
        if property_type:
            search_query = f"{search_query_base} {property_type} properties within {radius} mile radius"
        else:
            search_query = f"{search_query_base} properties within {radius} mile radius"
        
        # The agent should conduct a detailed comparison between the subject property and neighborhood
        result = (
            f"Detailed micro-market analysis for property at {property_location} "
            f"within a {radius} mile radius"
            f"{' focusing on '+property_type+' properties' if property_type else ''}:\n\n"
            f"The tool analyzes the immediate neighborhood surrounding the subject property. "
            f"The agent should extract and analyze: "
            f"- Comparison of subject property to neighboring properties\n"
            f"- Recent sales and listings within the {radius} mile radius\n"
            f"- Price per square foot and value trends in the immediate area\n"
            f"- Nearby amenities and points of interest\n"
            f"- Local infrastructure quality and accessibility\n"
            f"- Recent and planned development activity in the immediate vicinity\n"
            f"- Competitive advantages or disadvantages of the subject property\n"
            f"This analysis should highlight how the subject property compares to its immediate neighborhood."
        )
        
        return result 