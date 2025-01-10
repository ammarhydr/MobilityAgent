from crewai import Agent, Task, Crew
from .tools.mobility_inference_tool import MobilityInferenceTool

class AutomatingTransportationPlanningWithAgentModelsCrew:
    def __init__(self):
        # Initialize the MobilityInference tool
        self.mobility_tool = MobilityInferenceTool(
            model_path="path/to/your/model.pt",
            dataset="SF"
        )

    @agent
    def mobility_modeling_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['mobility_modeling_agent'],
            tools=[self.mobility_tool],
            verbose=True
        )

    @agent
    def real_time_traffic_integration_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['real_time_traffic_integration_agent'],
            
        )

    @agent
    def data_integration_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_integration_agent'],
            
        )

    @agent
    def traffic_optimization_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['traffic_optimization_agent'],
            
        )

    @agent
    def route_quality_assessment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['route_quality_assessment_agent'],
            
        )

    @task
    def convert_origin_input_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_origin_input_task'],
            tools=[JSONSearchTool()],
        )

    @task
    def generate_trajectories_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_trajectories_task'],
            
        )

    @task
    def fetch_traffic_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_traffic_data_task'],
            
        )

    @task
    def merge_datasets_task(self) -> Task:
        return Task(
            config=self.tasks_config['merge_datasets_task'],
            
        )

    @task
    def analyze_traffic_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_traffic_data_task'],
            
        )

    @task
    def evaluate_route_quality_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_route_quality_task'],
            
        )

    @task
    def generate_reports_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_reports_task'],
            
        )


    @crew
    def crew(self) -> Crew:
        """Creates the AutomatingTransportationPlanningWithAgentModels crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
