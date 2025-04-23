"""
Workforce assessment tools for Land Eval agents to analyze talent pools and educational resources.
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class WorkforceAssessmentInput(BaseModel):
    """Input schema for Workforce Assessment Tool."""
    location: str = Field(..., description="The location (City, State) to focus the assessment on.")
    industry_focus: str = Field(..., description="Optional industry sector to focus on (e.g., 'technology', 'manufacturing', 'healthcare').")

class WorkforceAssessmentTool(BaseTool):
    name: str = "Workforce and Educational Resources Assessment Tool"
    description: str = (
        "A specialized tool for analyzing workforce characteristics and educational resources "
        "in a particular location. This tool helps identify: "
        "1. Educational institutions and training programs in the area "
        "2. Workforce demographics including education levels and skill distribution "
        "3. Graduation rates and professional certifications in relevant fields "
        "4. Workforce development initiatives and programs "
        "5. Commuting patterns and labor shed analysis "
        "Use this tool to assess the availability of talent pools and how they might impact development potential."
    )
    args_schema: Type[BaseModel] = WorkforceAssessmentInput

    def _run(self, location: str, industry_focus: str = "") -> str:
        """
        Run the workforce assessment tool.
        
        Args:
            location: The city and state to focus on
            industry_focus: Optional industry sector to focus on
            
        Returns:
            Detailed information about workforce characteristics and educational resources
        """
        # Construct appropriate search query based on inputs
        if industry_focus:
            search_query = f"{location} workforce education labor demographics {industry_focus} talent training"
        else:
            search_query = f"{location} workforce education labor demographics talent training"
        
        # The agent should extract educational resources and workforce characteristics
        result = (
            f"Detailed workforce assessment for {location}"
            f"{' focusing on '+industry_focus if industry_focus else ''}:\n\n"
            f"The tool analyzes workforce characteristics, educational institutions, "
            f"and training programs in {location}. The agent should extract and analyze: "
            f"- Major educational institutions and their programs\n"
            f"- Workforce educational attainment levels\n"
            f"- Labor force participation rate and unemployment trends\n"
            f"- Average commute times and labor shed information\n"
            f"- Skills alignment with development needs\n"
            f"- Workforce development programs and initiatives\n"
            f"This analysis should assess how well the local workforce can support potential development."
        )
        
        return result 