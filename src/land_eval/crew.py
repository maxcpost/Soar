import warnings
import logging
import os
# Suppress specific warnings that might come from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="paramiko")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import CSVSearchTool
from crewai_tools import WebsiteSearchTool

# Import the custom tools
from src.land_eval.tools import EconomicGrowthResearchTool
from src.land_eval.tools import WorkforceAssessmentTool
from src.land_eval.tools import MicroMarketAnalysisTool

# Set up logger
logger = logging.getLogger(__name__)

# Define LLM selection logic
def get_llm_model():
    """
    Determine which LLM to use based on available API keys.
    Prefers Claude 3.5 Sonnet but falls back to GPT-4o if Anthropic key is not available.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key != "YOUR_ANTHROPIC_API_KEY_HERE":
        logger.info("Using Claude 3.5 Sonnet for enhanced reasoning capabilities")
        return "anthropic/claude-3-5-sonnet-20240620"
    else:
        logger.warning("Anthropic API key not available or invalid. Falling back to GPT-4o")
        return "gpt-4o"

# Get the LLM model to use across all agents
SELECTED_LLM = get_llm_model()

@CrewBase
class CrewAutomationEvaluationForLandListingOpportunitiesCrew():
    """CrewAutomationEvaluationForLandListingOpportunities crew"""

    @agent
    def property_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['property_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def environmental_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['environmental_evaluator'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def growth_trends_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['growth_trends_expert'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), EconomicGrowthResearchTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def occupancy_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['occupancy_expert'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def socio_economic_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['socio_economic_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def micro_market_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['micro_market_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), MicroMarketAnalysisTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def workforce_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['workforce_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), WorkforceAssessmentTool()],
            llm=SELECTED_LLM,
        )

    @agent
    def integrated_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['integrated_evaluator'],
            tools=[],
            llm=SELECTED_LLM,
        )

    @agent
    def narrative_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['narrative_reporter'],
            tools=[],
            llm=SELECTED_LLM,
        )


    @task
    def analyze_property_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_property_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
        )

    @task
    def analyze_environmental_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_environmental_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
        )

    @task
    def analyze_growth_trends_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_growth_trends_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), EconomicGrowthResearchTool()],
        )

    @task
    def analyze_housing_occupancy_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_housing_occupancy_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
        )

    @task
    def analyze_demographics_affordability_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_demographics_affordability_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
        )

    @task
    def analyze_micro_market_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_micro_market_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), MicroMarketAnalysisTool()],
        )

    @task
    def analyze_workforce_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_workforce_task'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), WorkforceAssessmentTool()],
        )

    @task
    def integrate_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['integrate_analysis_task'],
            tools=[],
        )

    @task
    def compile_narrative_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['compile_narrative_report_task'],
            tools=[],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the CrewAutomationEvaluationForLandListingOpportunities crew"""
        try:
            return Crew(
                agents=self.agents, # Automatically created by the @agent decorator
                tasks=self.tasks, # Automatically created by the @task decorator
                process=Process.sequential,
                verbose=True,
                memory=True,
                # Use the new chroma_vectordb directory instead of the default db directory
                memory_config={
                    "storage_type": "chroma",
                    "storage_path": "./chroma_vectordb"
                }
            )
        except Exception as e:
            logger.error(f"Error creating crew: {e}")
            # Return a simpler crew with reduced functionality as a fallback
            try:
                return Crew(
                    agents=self.agents, 
                    tasks=self.tasks,
                    process=Process.sequential,
                    verbose=True,
                    memory=False  # Disable memory to reduce dependencies
                )
            except Exception as fallback_error:
                logger.error(f"Critical error creating fallback crew: {fallback_error}")
                raise RuntimeError(f"Unable to create crew: {e}. Fallback also failed: {fallback_error}")
                
    def get_final_report_text(self, result):
        """
        Extract the final report from the crew execution result,
        handling various result formats and possible errors.
        
        Args:
            result: The result from crew.kickoff()
            
        Returns:
            str: The report content as a string
        """
        try:
            # Handle the case where result is already a string
            if isinstance(result, str):
                return result
            
            # If result has raw attribute with task_results
            if hasattr(result, 'raw') and isinstance(result.raw, dict):
                task_results = result.raw.get('task_results', [])
                
                # Look for the narrative_reporter task result
                for task in reversed(task_results):
                    if task.get('status') == 'completed':
                        output = task.get('output', '')
                        if output and isinstance(output, str):
                            # Extract Final Answer section if present
                            if 'Final Answer:' in output:
                                return output.split('Final Answer:', 1)[1].strip()
                            return output
            
            # Use str representation as fallback
            return str(result)
            
        except Exception as e:
            logger.error(f"Error extracting report text: {e}")
            return "Error extracting report content. See logs for details."
