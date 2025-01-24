import torch
import random
from mobilitygpt.model import GPT
from mobilitygpt.config import get_base_config
import pandas as pd
from typing import List

class MobilityInference:
    def __init__(self, 
                 model_path: str,
                 dataset: str = "SF"):
        """
        Initialize the MobilityInference model for generating synthetic trajectories.
        
        Args:
            model_path: Path to the trained model checkpoint
            dataset: Dataset name (default: "SF")
            device: Computing device to use (default: 'cuda' if available, else 'cpu')
        """

        
        # Initialize model configuration
        self.config = get_base_config()

        self.device = self.config.system.device 
        self.dataset = dataset
        
        # Load geography data
        self.geo = pd.read_csv(f'{dataset}-Taxi/roadmap.geo')
        self.geo_ids = self.geo['geo_id'].apply(str).tolist()
        
        # Load relationship data for adjacency matrix
        rel = pd.read_csv(f'{dataset}-Taxi/roadmap.rel')
        rel['combined'] = rel.apply(lambda x: [x['origin_id'], x['destination_id']], axis=1)
        od_list = rel['combined'].tolist()
        
        # Create adjacency matrix
        self.adj_matrix = self._create_adjacency_matrix(od_list)
        
        # Setup vocabulary
        self.EOS_TOKEN = '</S>'
        self.stoi = {ch: i for i, ch in enumerate(self.geo_ids)}
        self.itos = {i: ch for i, ch in enumerate(self.geo_ids)}
        self.stoi[self.EOS_TOKEN] = len(self.geo_ids)
        self.itos[len(self.geo_ids)] = self.EOS_TOKEN
        
        self.config.model.vocab_size = len(self.geo_ids)+1
        self.config.model.block_size = self.config.data.block_size 
        
        # Initialize and load model
        self.model = self._init_model(model_path)
        
    def _create_adjacency_matrix(self, od_pair_list):
        """Create adjacency matrix from OD pairs."""
        max_index = max(max(pair) for pair in od_pair_list)
        adjacency_matrix = torch.zeros((max_index + 1, max_index + 1), dtype=int)
        
        for origin, destination in od_pair_list:
            adjacency_matrix[origin, destination] = 1
            
        # Add boundary rows and columns
        adjacency_matrix = torch.cat((adjacency_matrix, torch.ones(1, adjacency_matrix.size(0))), 0)
        adjacency_matrix = torch.cat((adjacency_matrix, torch.ones(adjacency_matrix.size(0), 1)), 1)
        
        return adjacency_matrix.to(self.device)

    def _init_model(self, model_path: str):
        """Initialize and load the model."""
        model = GPT(self.config.model, adj_matrix=self.adj_matrix)
        model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        model.to(self.device)
        model.eval()
        return model

    def generate_trajectories(self, 
                            origin_id: str, 
                            num_trajectories: int = 1,
                            temperature: float = 1.0,
                            max_length: int = 81) -> List[List[int]]:
        """
        Generate synthetic trajectories from a given origin point.
        
        Args:
            origin_id: Starting road segment ID
            num_trajectories: Number of trajectories to generate
            temperature: Sampling temperature (higher = more random)
            max_length: Maximum trajectory length
            
        Returns:
            List of generated trajectories (each trajectory is a list of road segment IDs)
        """
        synthetic_trajectories = []
        
        for _ in range(num_trajectories):
            # Prepare context
            context = [self.EOS_TOKEN, str(origin_id)]
            x = torch.tensor([self.stoi[s] for s in context], dtype=torch.long)[None,...].to(self.device)
            
            # Generate trajectory
            with torch.no_grad():
                y = self.model.generate_test(
                    x, 
                    self.itos, 
                    self.EOS_TOKEN, 
                    max_token=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_k=None
                )[0]
            
            # Convert to road segment IDs
            trajectory = []
            for i in y[1:]:  # Skip first token
                if self.itos[int(i)] == self.EOS_TOKEN:
                    break
                trajectory.append(int(self.itos[int(i)]))
            
            synthetic_trajectories.append(trajectory)
            
        return synthetic_trajectories

    def get_segment_length(self, trajectory: List[int]) -> float:
        """Calculate the total length of a trajectory."""
        return self.geo[self.geo['geo_id'].isin(trajectory)].length.sum()