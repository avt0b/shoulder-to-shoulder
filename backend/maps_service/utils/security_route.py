"""
Security Route Calculator

Анализирует безопасность пешеходных маршрутов используя:
- OpenRouteService (маршруты)
- Overpass API (данные OSM - дороги, освещение)
- OpenRouter AI (комментарии)
"""

import json
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
import requests
from shapely.geometry import LineString, Point
import polyline

from ..config import settings

logger = logging.getLogger(__name__)


@dataclass
class RouteData:
    """Структура одного маршрута"""
    coordinates: List[Tuple[float, float]]  # [(lat, lon), ...]
    distance_m: float
    risk_score: float
    highway_type: str = "unknown"


@dataclass
class SafetyAnalysis:
    """Результат анализа безопасности"""
    safest_route: RouteData
    shortest_route: RouteData
    ai_comment: str
    all_routes: List[RouteData]


class SecurityRouteCalculator:
    """Основной класс для расчёта безопасных маршрутов"""
    
    # API endpoints
    OPENROUTE_URL = "https://api.openrouteservice.org/v2/directions/foot-walking"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self):
        self.api_key = settings.OPENROUTE_SERVICE_API_KEY
        self.ai_key = settings.OPENROUTER_API_KEY
        self.proxy_enabled = settings.PROXY_ENABLED
        self.proxies = self._get_proxies()
    
    def _get_proxies(self) -> Optional[Dict[str, str]]:
        """Получить прокси если включен"""
        if not self.proxy_enabled:
            return None
        
        return {
            "http": settings.PROXY_URL,
            "https": settings.PROXY_URL,
        }
    
    def get_routes(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> List[RouteData]:
        """Получить несколько альтернативных маршрутов от OpenRouteService"""
        try:
            headers = {
                "Authorization": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "coordinates": [
                    [start_lon, start_lat],
                    [end_lon, end_lat]
                ],
                "alternative_routes": {
                    "target_count": 3,
                    "weight_factor": 2,
                    "share_factor": 0.7
                },
                "instructions": False,
                "geometry": True
            }
            
            logger.info(f"📍 Запрашиваем маршруты: ({start_lat}, {start_lon}) → ({end_lat}, {end_lon})")
            response = requests.post(
                self.OPENROUTE_URL,
                json=body,
                headers=headers,
                proxies=self.proxies,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            routes = []
            for route in data.get("routes", []):
                coords = polyline.decode(route["geometry"])
                distance = route["summary"]["distance"]
                highway = route["summary"].get("highway_info", "unknown")
                
                routes.append(RouteData(
                    coordinates=coords,
                    distance_m=distance,
                    risk_score=0.0,  # Будет обновлено позже
                    highway_type=highway
                ))
            
            logger.info(f"✅ Получено {len(routes)} маршветов")
            return routes
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при запросе маршрутов: {e}")
            raise
    
    def get_osm_data(self, routes: List[RouteData]) -> Dict[str, Any]:
        """Получить данные OpenStreetMap вокруг маршрутов (дороги, фонари)"""
        try:
            # Выбираем точки вдоль маршрутов (каждая 7-я)
            sampled_points = []
            for route in routes:
                sampled_points.extend(route.coordinates[::7])
            
            logger.info(f"📍 Выбрано {len(sampled_points)} точек для анализа")
            
            # Строим Overpass запрос
            around_queries = ""
            for lat, lon in sampled_points:
                around_queries += f"""
                way(around:15,{lat},{lon})
                  ["highway"~"primary|secondary|tertiary|residential|footway"];
                node(around:15,{lat},{lon})
                  ["highway"="street_lamp"];
                """
            
            query = f"""
            [out:json][timeout:60];
            (
              {around_queries}
            );
            out geom;
            """
            
            logger.info("🔍 Запрашиваем данные Overpass API...")
            response = requests.post(
                self.OVERPASS_URL,
                data={"data": query},
                proxies=self.proxies,
                timeout=60
            )
            response.raise_for_status()
            
            osm_data = response.json()
            logger.info(f"✅ Получено {len(osm_data.get('elements', []))} элементов OSM")
            return osm_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка при запросе OSM данных: {e}")
            return {"elements": []}  # Возвращаем пустой результат
    
    def parse_osm_data(self, osm_data: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """Разбить OSM данные на дороги и уличные фонари"""
        street_lamps = []
        roads = []
        
        for el in osm_data.get("elements", []):
            if el["type"] == "node":
                tags = el.get("tags", {})
                if tags.get("highway") == "street_lamp":
                    street_lamps.append(el)
            
            elif el["type"] == "way":
                roads.append(el)
        
        logger.info(f"📊 Найдено: {len(roads)} дорог, {len(street_lamps)} фонарей")
        return roads, street_lamps
    
    def calculate_risk_score(self, route_coords: List[Tuple[float, float]], 
                            roads: List[Dict], lamps: List[Dict]) -> float:
        """Рассчитать риск для маршрута на основе дорог и освещения"""
        if not route_coords:
            return 100.0
        
        # GeoJSON формат: (lon, lat)
        route_line = LineString([(lon, lat) for lat, lon in route_coords])
        risk = 0.0
        
        # Анализируем дороги
        for way in roads:
            if "geometry" not in way:
                continue
            
            coords = [(pt["lon"], pt["lat"]) for pt in way["geometry"]]
            way_line = LineString(coords)
            
            # Если дорога далеко от маршрута - пропускаем
            if route_line.distance(way_line) > 0.00015:
                continue
            
            tags = way.get("tags", {})
            highway = tags.get("highway")
            lit = tags.get("lit")
            access = tags.get("access")
            
            # Опасные типы дорог
            if highway == "primary":
                risk += 3
            elif highway == "secondary":
                risk += 2
            elif highway == "tertiary":
                risk += 1
            
            # Возможное поражение от отсутствия освещения
            if lit == "no":
                risk += 3
            elif lit is None:  # Неизвестно
                risk += 1
            elif lit == "yes":
                risk -= 1  # Бонус за освещение
            
            # Приватные дороги опаснее
            if access == "private":
                risk += 2
        
        # Уличные фонари снижают риск
        for lamp in lamps:
            point = Point(lamp["lon"], lamp["lat"])
            if route_line.distance(point) < 0.0002:  # 20 метров
                risk -= 0.5
        
        # Минимум 0
        return max(0.0, risk)
    
    def get_ai_comment(self, routes: List[RouteData], safest_idx: int) -> str:
        """Получить AI комментарий о безопасности маршрута"""
        try:
            headers = {
                "Authorization": f"Bearer {self.ai_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "ShoulderToShoulder"
            }
            
            distances = [f"{r.distance_m:.0f}м" for r in routes]
            risks = [f"{r.risk_score:.1f}" for r in routes]
            
            prompt = f"""Ты помощник приложения для безопасных маршрутов. Приложение анализирует безопасность пешеходных маршрутов на основе:
- Типов дорог (из OSM)
- Наличия уличного освещения
- Количества уличных фонарей

Результаты для маршрутов (расстояния: {distances}, риск-оценка: {risks}):
Самый безопасный маршрут - маршрут {safest_idx+1} (индекс {safest_idx}).

Дай КОРОТКИЙ комментарий пользователю про безопасность ЭТО маршрута (не указывай номер).
Используй дружелюбный тон, упомяни дороги и освещение.

Ответ в JSON формате: {{"comment": "..."}}"""
            
            data = {
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150
            }
            
            logger.info("🤖 Запрашиваем AI комментарий...")
            response = requests.post(
                self.OPENROUTER_URL,
                headers=headers,
                json=data,
                proxies=self.proxies,
                timeout=20
            )
            response.raise_for_status()
            
            resp = response.json()
            content = resp["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            comment = parsed.get("comment", "Маршрут доступен для пешеходов.")
            
            logger.info(f"✅ AI комментарий получен")
            return comment
            
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при получении AI комментария: {e}")
            return "Маршрут проанализирован. Следите за дорожной обстановкой."
    
    async def calculate_safe_route(self, start_lat: float, start_lon: float, 
                                   end_lat: float, end_lon: float) -> SafetyAnalysis:
        """Главный метод: рассчитать безопасный маршрут"""
        try:
            # 1. Получить маршруты
            routes = self.get_routes(start_lat, start_lon, end_lat, end_lon)
            
            if not routes:
                raise ValueError("Маршруты не найдены")
            
            # 2. Получить OSM данные
            osm_data = self.get_osm_data(routes)
            roads, lamps = self.parse_osm_data(osm_data)
            
            # 3. Рассчитать риск для каждого маршрута
            for route in routes:
                route.risk_score = self.calculate_risk_score(route.coordinates, roads, lamps)
            
            # 4. Найти лучшие маршруты
            safest_route = min(routes, key=lambda r: r.risk_score)
            shortest_route = min(routes, key=lambda r: r.distance_m)
            
            # 5. Получить AI комментарий
            safest_idx = routes.index(safest_route)
            ai_comment = self.get_ai_comment(routes, safest_idx)
            
            logger.info(f"✅ Анализ завершён! Самый безопасный маршрут имеет риск {safest_route.risk_score:.1f}")
            
            return SafetyAnalysis(
                safest_route=safest_route,
                shortest_route=shortest_route,
                ai_comment=ai_comment,
                all_routes=routes
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка при расчёте маршрута: {e}")
            raise


# Singleton экземпляр
_calculator = None


def get_calculator() -> SecurityRouteCalculator:
    """Получить singleton экземпляр"""
    global _calculator
    if _calculator is None:
        _calculator = SecurityRouteCalculator()
    return _calculator
