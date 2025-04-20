import warnings
import logging
# Suppress specific warnings that might come from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="paramiko")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import CSVSearchTool
from crewai_tools import WebsiteSearchTool

# Import the custom research tool
from src.land_eval.tools import EconomicGrowthResearchTool

# Set up logger
logger = logging.getLogger(__name__)

@CrewBase
class CrewAutomationEvaluationForLandListingOpportunitiesCrew():
    """CrewAutomationEvaluationForLandListingOpportunities crew"""

    @agent
    def property_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['property_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm="gpt-4o",
        )

    @agent
    def environmental_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['environmental_evaluator'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm="gpt-4o",
        )

    @agent
    def growth_trends_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['growth_trends_expert'],
            tools=[CSVSearchTool(), WebsiteSearchTool(), EconomicGrowthResearchTool()],
            llm="gpt-4o",
        )

    @agent
    def occupancy_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['occupancy_expert'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm="gpt-4o",
        )

    @agent
    def socio_economic_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['socio_economic_analyst'],
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm="gpt-4o",
        )

    @agent
    def integrated_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['integrated_evaluator'],
            tools=[],
            llm="gpt-4o",
        )

    @agent
    def narrative_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['narrative_reporter'],
            tools=[],
            llm="gpt-4o",
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
