import warnings
# Suppress specific warnings that might come from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="paramiko")
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import CSVSearchTool
from crewai_tools import WebsiteSearchTool

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
            tools=[CSVSearchTool(), WebsiteSearchTool()],
            llm="gpt-4o",
        )

    @agent
    def occupancy_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['occupancy_expert'],
            tools=[CSVSearchTool()],
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
            tools=[CSVSearchTool(), WebsiteSearchTool()],
        )

    @task
    def analyze_housing_occupancy_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_housing_occupancy_task'],
            tools=[CSVSearchTool()],
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
