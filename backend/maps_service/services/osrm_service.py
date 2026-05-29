import requests
from typing import Dict, List, Tuple, Optional


class OSRMService:
    BASE_URL = "https://router.project-osrm.org/route/v1/foot"
    
    @staticmethod
    def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict:
        url = f"{OSRMService.BASE_URL}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("code") != "Ok":
                raise Exception("OSRM error")
            
            route_data = data["routes"][0]
            
            return {
                "distance": route_data["distance"],
                "duration": route_data["duration"],
                "geometry": route_data["geometry"],
                "steps": OSRMService._parse_steps(route_data.get("legs", [])),
            }
        except Exception as e:
            raise Exception(f"Failed to get route: {str(e)}")
    
    @staticmethod
    def _parse_steps(legs: List) -> List[Dict]:
        steps = []
        for leg in legs:
            for step in leg.get("steps", []):
                steps.append({
                    "instruction": step.get("maneuver", {}).get("instruction", "Продолжайте"),
                    "distance": step.get("distance", 0),
                    "duration": step.get("duration", 0),
                })
        return steps
    
    @staticmethod
    def get_coordinates_from_route(start_lat: float, start_lon: float, 
                                   end_lat: float, end_lon: float) -> List[Tuple]:
        route_data = OSRMService.get_route(start_lat, start_lon, end_lat, end_lon)
        geometry = route_data["geometry"]
        
        if geometry["type"] == "LineString":
            return geometry["coordinates"]
        return []
