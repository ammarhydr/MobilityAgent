from crewai.tools import BaseTool
from typing import List, Tuple, Dict, Optional, Type
from pydantic import BaseModel, Field, ConfigDict
import requests
from math import radians, cos, sin, asin, sqrt
import os
from dotenv import load_dotenv

class Coordinate(BaseModel):
    """Schema for coordinate pairs"""
    latitude: float = Field(..., description="Latitude", alias="latitude")
    longitude: float = Field(..., description="Longitude", alias="longitude")
    
    model_config = ConfigDict(populate_by_name=True)

class RouteQualityInput(BaseModel):
    """Input schema for RouteQualityTool."""
    coordinates: List[Coordinate] = Field(
        ..., 
        description="List of coordinate pairs (latitude, longitude)"
    )
    actual_times: Optional[List[float]] = Field(
        default=None, 
        description="Optional list of actual travel times between points"
    )

class RouteQualityTool(BaseTool):
    name: str = "Route Quality Analyzer"
    description: str = (
        "A tool for evaluating route quality by comparing trajectories with Google Maps data. "
        "Analyzes distances, durations, and traffic conditions along the route."
    )
    args_schema: Type[BaseModel] = RouteQualityInput
    api_key: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        super().__init__()
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key not found in environment variables")

    def _run(
        self,
        coordinates: List[Coordinate],
        actual_times: Optional[List[float]] = None
    ) -> str:
        """
        Run the route quality analysis.
        
        Args:
            coordinates: List of Coordinate objects containing lat/lon pairs
            actual_times: Optional list of actual travel times between points
            
        Returns:
            Formatted string containing route quality metrics
        """
        # Ensure coordinates are properly processed
        if isinstance(coordinates, list) and all(isinstance(coord, dict) for coord in coordinates):
            # Handle dict input
            trajectory = [(float(coord['latitude']), float(coord['longitude'])) for coord in coordinates]
        else:
            # Handle Coordinate model input
            trajectory = [(float(coord.latitude), float(coord.longitude)) for coord in coordinates]
        
        try:
            metrics = self.evaluate_route_quality(trajectory, actual_times)
            
            if "error" in metrics:
                return f"Error: {metrics['error']}"
            
            # Format the output
            output = "Route Quality Analysis:\n\n"
            output += f"Total Distance (Actual): {metrics['total_distance_actual']:.2f} meters\n"
            output += f"Total Distance (Google): {metrics['total_distance_google']:.2f} meters\n"
            output += f"Route Efficiency: {metrics.get('route_efficiency', 'N/A'):.2f}\n"
            output += f"Traffic Impact: {metrics.get('traffic_impact', 'N/A'):.2f}\n\n"
            
            output += "Segment Analysis:\n"
            for segment in metrics['segments'][:5]:  # Show first 5 segments
                output += f"\nSegment {segment['segment_id']}:\n"
                output += f"  From: {segment['start_address']}\n"
                output += f"  To: {segment['end_address']}\n"
                output += f"  Distance (Actual): {segment['actual_distance']:.2f} meters\n"
                output += f"  Distance (Google): {segment['google_distance']:.2f} meters\n"
                output += f"  Duration: {segment['google_duration'] // 60} minutes\n"
                output += f"  Duration with Traffic: {segment['traffic_duration'] // 60} minutes\n"
            
            if len(metrics['segments']) > 5:
                output += f"\n... and {len(metrics['segments']) - 5} more segments"
            
            return output
            
        except Exception as e:
            return f"Error analyzing route quality: {str(e)}"

    def get_google_maps_route(self, origin: Tuple[float, float], 
                            destination: Tuple[float, float]) -> Optional[Dict]:
        """
        Fetches route information from Google Maps Directions API.
        
        Args:
            origin: Starting point (latitude, longitude)
            destination: Ending point (latitude, longitude)
            
        Returns:
            Dictionary with route information or None if request fails
        """
        url = (f"https://maps.googleapis.com/maps/api/directions/json?"
               f"origin={origin[0]},{origin[1]}&"
               f"destination={destination[0]},{destination[1]}&"
               f"departure_time=now&key={self.api_key}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                route = data['routes'][0]
                leg = route['legs'][0]
                return {
                    'duration': leg['duration']['value'],
                    'duration_in_traffic': leg['duration_in_traffic']['value'],
                    'distance': leg['distance']['value'],
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'steps': leg['steps']
                }
            print(f"Google Maps API Error: {data['status']}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None

    @staticmethod
    def haversine_distance(coord1: Tuple[float, float], 
                          coord2: Tuple[float, float]) -> float:
        """
        Calculates Haversine distance between two coordinates.
        
        Args:
            coord1: (latitude1, longitude1)
            coord2: (latitude2, longitude2)
            
        Returns:
            Distance in meters
        """
        R = 6371000  # Earth's radius in meters

        lat1, lon1 = map(radians, coord1)
        lat2, lon2 = map(radians, coord2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        return R * c

    def evaluate_route_quality(self, trajectory: List[Tuple[float, float]], 
                             actual_times: Optional[List[float]] = None) -> Dict:
        """
        Evaluates the quality of a route by comparing it with Google Maps suggestions.
        
        Args:
            trajectory: List of (latitude, longitude) coordinates
            actual_times: Optional list of actual travel times between points
            
        Returns:
            Dictionary containing quality metrics
        """
        if len(trajectory) < 2:
            return {"error": "Trajectory must contain at least 2 points"}

        metrics = {
            'total_distance_actual': 0,
            'total_distance_google': 0,
            'total_time_google': 0,
            'total_time_traffic': 0,
            'segments': []
        }

        for i in range(len(trajectory) - 1):
            start = trajectory[i]
            end = trajectory[i + 1]
            
            # Calculate actual distance using Haversine
            actual_distance = self.haversine_distance(start, end)
            metrics['total_distance_actual'] += actual_distance

            # Get Google Maps route data
            route_info = self.get_google_maps_route(start, end)
            if route_info:
                metrics['total_distance_google'] += route_info['distance']
                metrics['total_time_google'] += route_info['duration']
                metrics['total_time_traffic'] += route_info['duration_in_traffic']
                
                segment_metrics = {
                    'segment_id': i,
                    'start_point': start,
                    'end_point': end,
                    'actual_distance': actual_distance,
                    'google_distance': route_info['distance'],
                    'google_duration': route_info['duration'],
                    'traffic_duration': route_info['duration_in_traffic'],
                    'start_address': route_info['start_address'],
                    'end_address': route_info['end_address']
                }
                
                if actual_times and len(actual_times) > i:
                    segment_metrics['actual_duration'] = actual_times[i]
                
                metrics['segments'].append(segment_metrics)

        # Calculate aggregate metrics
        if metrics['segments']:
            metrics['route_efficiency'] = (
                metrics['total_distance_google'] / metrics['total_distance_actual']
            )
            metrics['traffic_impact'] = (
                metrics['total_time_traffic'] / metrics['total_time_google']
            )

        return metrics