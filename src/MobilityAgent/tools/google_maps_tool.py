from crewai.tools import BaseTool
from typing import Type, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict
import requests
import os
from dotenv import load_dotenv

class GoogleMapsInput(BaseModel):
    """Input schema for GoogleMapsTool."""
    origin: str = Field(..., description="Starting point (e.g., 'Columbus Ave, San Francisco, CA')")
    destination: str = Field(..., description="Ending point (e.g., 'Market St, San Francisco, CA')")
    departure_time: str = Field(default="now", description="Departure time (default is current time)")

class GoogleMapsTool(BaseTool):
    name: str = "Google Maps Traffic Data Fetcher"
    description: str = (
        "A tool for fetching real-time traffic data using Google Maps API. "
        "Provides traffic information including duration with and without traffic, "
        "and traffic delays between two points."
    )
    args_schema: Type[BaseModel] = GoogleMapsInput
    api_key: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key not found in environment variables")

    def _get_traffic_info(self, origin: str, destination: str) -> Optional[Dict]:
        """
        Fetches traffic information using Google Maps Directions API.
        
        Args:
            origin: Starting point
            destination: Ending point
            
        Returns:
            Dictionary containing traffic information or None if request fails
        """
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json"
            f"?origin={origin}&destination={destination}"
            f"&departure_time=now&key={self.api_key}"
        )
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data['status'] == 'OK':
                route = data['routes'][0]
                leg = route['legs'][0]
                
                duration = leg['duration']['value']
                duration_in_traffic = leg['duration_in_traffic']['value']
                traffic_delay = duration_in_traffic - duration
                
                distance = leg['distance']['text']
                start_address = leg['start_address']
                end_address = leg['end_address']
                
                return {
                    'duration': duration,
                    'duration_in_traffic': duration_in_traffic,
                    'traffic_delay': traffic_delay,
                    'distance': distance,
                    'start_address': start_address,
                    'end_address': end_address,
                    'steps': leg.get('steps', [])
                }
            else:
                print(f"Google Maps API Error: {data['status']}") 
                return None
                
        except requests.exceptions.RequestException as e:
            return None

    def _run(
        self, 
        origin: str,
        destination: str,
        departure_time: str = "now"
    ) -> str:
        """
        Run the Google Maps tool to fetch traffic data.
        
        Args:
            origin: Starting point
            destination: Ending point
            departure_time: Time of departure (default: "now")
            
        Returns:
            Formatted string containing traffic information
        """
        try:
            traffic_data = self._get_traffic_info(origin, destination)
            
            if not traffic_data:
                return "Error: Unable to fetch traffic data from Google Maps API"
            
            # Format the output
            output = "Traffic Information:\n\n"
            output += f"Route: {traffic_data['start_address']} → {traffic_data['end_address']}\n"
            output += f"Distance: {traffic_data['distance']}\n"
            output += f"Duration without traffic: {traffic_data['duration'] // 60} minutes\n"
            output += f"Duration with traffic: {traffic_data['duration_in_traffic'] // 60} minutes\n"
            output += f"Traffic delay: {traffic_data['traffic_delay'] // 60} minutes\n\n"
            
            # Add route steps if available
            if traffic_data['steps']:
                output += "Route Steps:\n"
                for i, step in enumerate(traffic_data['steps'], 1):
                    output += f"{i}. {step['html_instructions']}\n"
            
            return output
            
        except Exception as e:
            return f"Error fetching traffic data: {str(e)}"