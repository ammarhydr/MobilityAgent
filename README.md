# MobilityAgent

MobilityAgent is an AI-powered transportation analysis system built on [crewAI](https://crewai.com) that leverages [MobilityGPT](https://github.com/AmmarHaydari/MobilityGPT) for trajectory generation and integrates real-time traffic data for comprehensive mobility solutions in San Francisco.

## Architecture Overview

MobilityAgent employs a multi-agent system architecture where specialized AI agents work together to:
1. Convert natural language locations to road segments
2. Generate synthetic trajectories using MobilityGPT
3. Integrate real-time traffic data
4. Assess route quality
5. Compile comprehensive reports

### Agent Roles & Responsibilities

- **Location Translation Specialist**
  - Converts natural language addresses to road segment IDs
  - Uses geospatial mapping and urban network knowledge
  - Ensures accurate location interpretation

- **Trajectory Generation Expert**
  - Leverages MobilityGPT for synthetic trajectory creation
  - Simulates realistic traffic patterns
  - Generates route variations based on historical data

- **Traffic Data Specialist**
  - Integrates Google Maps API real-time data
  - Monitors current traffic conditions
  - Enriches synthetic trajectories with live data

- **Route Quality Evaluator**
  - Assesses generated routes against real-world conditions
  - Analyzes metrics like distance accuracy and time efficiency
  - Provides quality scores for trajectories

- **Transportation Data Integration Specialist**
  - Compiles analyses into actionable reports
  - Generates optimization suggestions
  - Creates markdown-formatted comprehensive summaries

## Prerequisites

- Python 3.9+
- Google Maps API key
- MobilityGPT model

## Running


```bash
python src/mobilityagent/main.py run  
```