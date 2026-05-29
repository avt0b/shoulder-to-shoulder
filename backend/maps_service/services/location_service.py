from typing import Dict, List, Tuple
from math import radians, sin, cos, sqrt, atan2


class LocationService:
    """Сервис для работы с геолокацией и координатами"""
    
    EARTH_RADIUS_KM = 6371  # Радиус Земли в км
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Вычислить расстояние между двумя точками на Земле в км.
        Использует формулу Хаверсина.
        """
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return LocationService.EARTH_RADIUS_KM * c
    
    @staticmethod
    def find_nearby_users(user_location: Tuple[float, float],
                         other_users: List[Dict],
                         radius_km: float = 1.0) -> List[Dict]:
        """
        Найти пользователей рядом с указанной локацией.
        
        Args:
            user_location: кортеж (lat, lon) пользователя
            other_users: список пользователей с их локациями
            radius_km: радиус поиска в км
        
        Returns:
            Список пользователей в радиусе с расстояниями
        """
        nearby = []
        user_lat, user_lon = user_location
        
        for other_user in other_users:
            distance = LocationService.calculate_distance(
                user_lat, user_lon,
                other_user['latitude'], other_user['longitude']
            )
            
            if distance <= radius_km:
                nearby.append({
                    **other_user,
                    'distance_km': round(distance, 2)
                })
        
        # Сортируем по расстоянию
        nearby.sort(key=lambda x: x['distance_km'])
        return nearby
    
    @staticmethod
    def calculate_center_point(locations: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Вычислить центральную точку между несколькими локациями.
        """
        if not locations:
            raise ValueError("Список локаций не может быть пустым")
        
        avg_lat = sum(loc[0] for loc in locations) / len(locations)
        avg_lon = sum(loc[1] for loc in locations) / len(locations)
        
        return (avg_lat, avg_lon)
    
    @staticmethod
    def is_valid_coordinates(latitude: float, longitude: float) -> bool:
        """Проверить, валидны ли координаты"""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    @staticmethod
    def get_bounding_box(center_lat: float, center_lon: float, 
                        radius_km: float) -> Dict[str, float]:
        """
        Получить bounding box вокруг центральной точки.
        Это упрощённый расчёт (не учитывает сферичность Земли).
        """
        # Примерно 1 градус на экваторе = 111.32 км
        degrees_per_km = 1 / 111.32
        
        delta = radius_km * degrees_per_km
        
        return {
            'min_latitude': center_lat - delta,
            'max_latitude': center_lat + delta,
            'min_longitude': center_lon - delta,
            'max_longitude': center_lon + delta,
        }
    
    @staticmethod
    def bearing_between_points(lat1: float, lon1: float, 
                               lat2: float, lon2: float) -> float:
        """
        Вычислить азимут (bearing) от точки 1 к точке 2 в градусах (0-360).
        """
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lon = radians(lon2 - lon1)
        
        x = sin(delta_lon) * cos(lat2_rad)
        y = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(delta_lon)
        
        bearing_rad = atan2(x, y)
        bearing_deg = (bearing_rad * 180 / 3.14159265359 + 360) % 360
        
        return bearing_deg
