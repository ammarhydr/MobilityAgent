from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from ..mobility_inference import MobilityInference

class MobilityInferenceInput(BaseModel):
    """Input schema for MobilityInferenceTool."""
    origin_id: str = Field(..., description="Starting road segment ID for trajectory generation")
    num_trajectories: int = Field(default=100, description="Number of trajectories to generate")
    temperature: float = Field(default=1.0, description="Sampling temperature (higher = more random)")
    max_length: int = Field(default=81, description="Maximum trajectory length")

class MobilityInferenceTool(BaseTool):
    name: str = "Mobility Trajectory Generator"
    description: str = (
        "A tool for generating synthetic mobility trajectories from a given origin point. "
        "It uses a trained MobilityGPT model to generate realistic traffic patterns. "
        "Input should be a road segment ID, and it will return a list of possible trajectories."
    )
    args_schema: Type[BaseModel] = MobilityInferenceInput
    
    def __init__(self, model_path: str, dataset: str = "SF"):
        super().__init__()
        self.inference_model = MobilityInference(
            model_path=model_path,
            dataset=dataset
        )

    def _run(
        self, 
        origin_id: str, 
        num_trajectories: int = 100,
        temperature: float = 1.0,
        max_length: int = 81
    ) -> str:
        """
        Generate trajectories using MobilityGPT model.
        
        Args:
            origin_id: Starting road segment ID
            num_trajectories: Number of trajectories to generate
            temperature: Sampling temperature
            max_length: Maximum trajectory length
            
        Returns:
            A formatted string containing the generated trajectories and their lengths
        """
        try:
            trajectories = self.inference_model.generate_trajectories(
                origin_id=origin_id,
                num_trajectories=num_trajectories,
                temperature=temperature,
                max_length=max_length
            )
            
            # Format the output
            output = f"Generated {len(trajectories)} trajectories from origin {origin_id}:\n\n"
            for i, trajectory in enumerate(trajectories[:5], 1):  # Show first 5 trajectories
                length = self.inference_model.get_segment_length(trajectory)
                output += f"Trajectory {i}: {trajectory}\n"
                output += f"Length: {length:.2f} units\n\n"
            
            if len(trajectories) > 5:
                output += f"... and {len(trajectories) - 5} more trajectories\n"
                
            return output
            
        except Exception as e:
            return f"Error generating trajectories: {str(e)}" 