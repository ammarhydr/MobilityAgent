# Mobility Agent

Welcome to the MobilityAgent project, powered by [crewAI](https://crewai.com). 

## Overview

MobilityAgent is an advanced AI-powered transportation planning system that leverages multiple specialized agents to analyze and optimize traffic patterns in San Francisco. The system integrates synthetic trajectory generation with real-time traffic data to provide comprehensive mobility solutions.

### Key Features

- **Synthetic Trajectory Generation**: Uses MobilityGPT to create realistic traffic patterns and movement scenarios
- **Real-Time Traffic Integration**: Incorporates live traffic data from Google Maps API
- **Data Integration & Analysis**: Seamlessly merges synthetic and real-time data for comprehensive analysis
- **Traffic Optimization**: Provides data-driven suggestions for improving traffic flow
- **Route Quality Assessment**: Evaluates generated routes against real-world conditions

### Agent Roles

The system employs six specialized AI agents:

1. **Coordination Specialist**: Orchestrates the overall analysis process and delegates tasks among other agents

2. **Trajectory Generation Expert**: Creates synthetic traffic patterns using MobilityGPT, simulating various scenarios for specific road segments

3. **Traffic Data Specialist**: Gathers and processes real-time traffic information from Google Maps API

4. **Data Integration Specialist**: Combines synthetic trajectories with real-time data to create a unified view of traffic dynamics

5. **Traffic Analysis Expert**: Analyzes the integrated data to identify optimization opportunities

6. **Route Quality Evaluator**: Assesses the quality and efficiency of generated routes by comparing them with Google Maps data


## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

- Modify `src/automating_transportation_planning_with_agent_models/config/agents.yaml` to define your agents
- Modify `src/automating_transportation_planning_with_agent_models/config/tasks.yaml` to define your tasks
- Modify `src/automating_transportation_planning_with_agent_models/crew.py` to add your own logic, tools and specific args
- Modify `src/automating_transportation_planning_with_agent_models/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the automating_transportation_planning_with_agent_models Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.
