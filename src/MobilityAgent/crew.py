from crewai import Agent, Task, Crew, Process
from crewai.tools import JSONSearchTool
from .tools.mobility_inference_tool import MobilityInferenceTool
from .tools.google_maps_tool import GoogleMapsTool

class MobilityAgentCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Initialize the MobilityInference tool
        self.mobility_tool = MobilityInferenceTool(
            model_path="path/to/your/model.pt",
            dataset="SF"
        )
        self.google_maps_tool = GoogleMapsTool()

    @agent
    def agent_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_manager'],
            tools=[self.mobility_tool],
            verbose=True
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
            tools=[self.google_maps_tool],
            verbose=True
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

    @agent
    def information_compiler_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['information_compiler_agent'],
            
        )

    @task
    def convert_origin_input_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_origin_input_task'],
            tools=[JSONSearchTool()],
            agent=self.agent_manager()
        )

    @task
    def generate_trajectories_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_trajectories_task'],
            agent=self.mobility_modeling_agent()
        )

    @task
    def fetch_traffic_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_traffic_data_task'],
            agent=self.real_time_traffic_integration_agent()
        )

    @task
    def analyze_traffic_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_traffic_data_task'],
            agent=self.traffic_optimization_agent()
        )

    @task
    def evaluate_route_quality_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_route_quality_task'],
            agent=self.route_quality_assessment_agent()
        )

    @task
    def generate_reports_task(self) -> Task:
        return Task(
            config=self.tasks_config['generate_reports_task'],
            agent=self.information_compiler_agent()
        )


    @crew
    def crew(self) -> Crew:
        """Creates the MobilityAgents crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
