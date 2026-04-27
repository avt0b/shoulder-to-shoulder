from typing import Dict, List, Tuple, Optional
from ..models.schemas import SafeRouteSchema
from .location_service import LocationService


class RouteService:
    """Сервис для работы с маршрутами и построением безопасных путей"""
    
    def __init__(self):
        self.location_service = LocationService()
    
    async def find_safe_route(self,
                             origin_lat: float,
                             origin_lon: float,
                             destination_lat: float,
                             destination_lon: float,
                             safe_zones: Optional[List[Dict]] = None,
                             unsafe_zones: Optional[List[Dict]] = None) -> SafeRouteSchema:
        """
        Построить безопасный маршрут от начальной точки к конечной.
        
        Args:
            origin_lat, origin_lon: начальные координаты
            destination_lat, destination_lon: конечные координаты
            safe_zones: список безопасных зон (с координатами)
            unsafe_zones: список небезопасных зон (избегать при маршруте)
        
        Returns:
            Маршрут с оценкой безопасности
        """
        distance = self.location_service.calculate_distance(
            origin_lat, origin_lon,
            destination_lat, destination_lon
        )
        
        # Вычисляем оценку безопасности (от 0 до 1)
        safety_score = self._calculate_safety_score(
            origin_lat, origin_lon,
            destination_lat, destination_lon,
            safe_zones or [],
            unsafe_zones or []
        )
        
        route = SafeRouteSchema(
            origin={'latitude': origin_lat, 'longitude': origin_lon},
            destination={'latitude': destination_lat, 'longitude': destination_lon},
            description=self._generate_route_description(distance, safety_score),
            safe_score=safety_score
        )
        
        return route
    
    async def synchronize_group_departure(self,
                                         users_locations: List[Dict],
                                         target_location: Tuple[float, float],
                                         meeting_time_minutes: int = 15) -> Dict:
        """
        Синхронизировать выход группы из разных мест в один пункт.
        Рассчитать время для каждого пользователя, чтобы всем прийти одновременно.
        
        Args:
            users_locations: список юзеров с их координатами
            target_location: целевая локация (lat, lon)
            meeting_time_minutes: через сколько минут встреча
        
        Returns:
            Расписание выхода для каждого пользователя
        """
        schedule = {}
        average_walking_speed_kmh = 5  # Среднняя скорость пешком
        
        for user in users_locations:
            distance = self.location_service.calculate_distance(
                user['latitude'], user['longitude'],
                target_location[0], target_location[1]
            )
            
            # Время в пути в минутах
            travel_time = (distance / average_walking_speed_kmh) * 60
            
            # Время выхода = время встречи - время в пути
            departure_delay = max(0, meeting_time_minutes - travel_time)
            
            schedule[user['user_id']] = {
                'distance_km': round(distance, 2),
                'travel_time_minutes': round(travel_time, 1),
                'departure_delay_minutes': round(departure_delay, 1),
                'should_wait_minutes': round(max(0, travel_time - meeting_time_minutes), 1)
            }
        
        return schedule
    
    async def find_meeting_point(self,
                                users_locations: List[Tuple[float, float]]) -> Dict:
        """
        Найти оптимальную точку встречи для группы пользователей.
        """
        center = self.location_service.calculate_center_point(users_locations)
        
        max_distance = 0
        for user_loc in users_locations:
            distance = self.location_service.calculate_distance(
                center[0], center[1],
                user_loc[0], user_loc[1]
            )
            max_distance = max(max_distance, distance)
        
        return {
            'center_latitude': center[0],
            'center_longitude': center[1],
            'max_distance_from_center_km': round(max_distance, 2),
            'user_count': len(users_locations)
        }
    
    @staticmethod
    def _calculate_safety_score(origin_lat: float, origin_lon: float,
                               destination_lat: float, destination_lon: float,
                               safe_zones: List[Dict],
                               unsafe_zones: List[Dict]) -> float:
        """
        Вычислить оценку безопасности маршрута от 0 до 1.
        
        Логика:
        - По умолчанию 0.7 (нейтрально)
        - +0.2 за каждую безопасную зону на пути
        - -0.3 за каждую небезопасную зону на пути
        """
        score = 0.7
        
        # Проверяем пересечение с безопасными зонами
        for zone in safe_zones:
            if RouteService._is_route_crossing_zone(
                origin_lat, origin_lon,
                destination_lat, destination_lon,
                zone.get('latitude'), zone.get('longitude'),
                zone.get('radius_km', 0.5)
            ):
                score += 0.2
        
        # Проверяем пересечение с небезопасными зонами
        for zone in unsafe_zones:
            if RouteService._is_route_crossing_zone(
                origin_lat, origin_lon,
                destination_lat, destination_lon,
                zone.get('latitude'), zone.get('longitude'),
                zone.get('radius_km', 0.5)
            ):
                score -= 0.3
        
        # Ограничиваем оценку от 0 до 1
        return max(0.0, min(1.0, score))
    
    @staticmethod
    def _is_route_crossing_zone(origin_lat: float, origin_lon: float,
                               dest_lat: float, dest_lon: float,
                               zone_lat: float, zone_lon: float,
                               radius_km: float) -> bool:
        """
        Проверить, пересекает ли маршрут зону.
        Упрощённая версия - проверяет расстояние от центра зоны до линии маршрута.
        """
        # Расстояние от начала до конца
        route_distance = LocationService.calculate_distance(
            origin_lat, origin_lon, dest_lat, dest_lon
        )
        
        # Расстояние от начала до центра зоны
        origin_to_zone = LocationService.calculate_distance(
            origin_lat, origin_lon, zone_lat, zone_lon
        )
        
        # Расстояние от конца до центра зоны
        dest_to_zone = LocationService.calculate_distance(
            dest_lat, dest_lon, zone_lat, zone_lon
        )
        
        # Если хотя бы один из этих расстояний меньше радиуса, маршрут пересекает зону
        return origin_to_zone <= radius_km or dest_to_zone <= radius_km
    
    @staticmethod
    def _generate_route_description(distance_km: float, safety_score: float) -> str:
        """Генерировать описание маршрута"""
        safety_level = "Высокий" if safety_score >= 0.8 else "Средний" if safety_score >= 0.5 else "Низкий"
        return f"Расстояние: {distance_km:.1f} км, уровень безопасности: {safety_level}"
