from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, crew, task
from src.mobilityagent.tools.mobility_inference_tool import MobilityInferenceTool
from src.mobilityagent.tools.google_maps_tool import GoogleMapsTool
from src.mobilityagent.tools.route_quality_tool import RouteQualityTool
from src.mobilityagent.tools.location_link_tool import LocationToLinkTool
from src.mobilityagent.tools.link_location_tool import LinkToLocationTool
from crewai_tools import SerperDevTool


@CrewBase
class MobilityAgentCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Initialize the MobilityInference tool
        self.mobility_tool = MobilityInferenceTool(
            model_path="mobilitygpt/model.pt",
            dataset="SF"
        )
        self.google_maps_tool = GoogleMapsTool()
        self.route_quality_tool = RouteQualityTool()
        self.serper_tool = SerperDevTool()
        self.location2link_tool = LocationToLinkTool(
            graph_path="SF-Taxi/graph.csv")
        self.link2location_tool = LinkToLocationTool(
             graph_path="SF-Taxi/graph.csv")

    @agent
    def location_translator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['location_translator_agent'],
            tools=[self.location2link_tool],
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
            tools=[self.google_maps_tool, self.link2location_tool],
            verbose=True
        )

    @agent
    def route_quality_assessment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['route_quality_assessment_agent'],
            tools=[self.route_quality_tool],
            verbose=True
        )

    @agent
    def information_compiler_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['information_compiler_agent'],
            tools=[self.serper_tool],
            verbose=True
        )

    @task
    def convert_origin_input_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_origin_input_task'],
            agent=self.location_translator_agent()
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
