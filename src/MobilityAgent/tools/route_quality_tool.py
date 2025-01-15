import requests
from math import radians, cos, sin, asin, sqrt
from typing import List, Tuple, Dict, Optional

class RouteQualityTool:
    def __init__(self, api_key: str):
        self.api_key = api_key

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