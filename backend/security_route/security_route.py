import json
from shapely.geometry import LineString, Point
import polyline
import requests


API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjgyYTgzYjc5NDBiNjRlMjE5Njk0MjM1ZmNjMjFkZDlhIiwiaCI6Im11cm11cjY0In0="
OPENROUTER_API_KEY = "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"


proxies = {
    "http": "socks5h://127.0.0.1:12334",
    "https": "socks5h://127.0.0.1:12334",
}

def get_route(start_lat, start_lon, end_lat, end_lon):

    url = "https://api.openrouteservice.org/v2/directions/foot-walking"

    headers = {
        "Authorization": API_KEY,
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

    response = requests.post(url, json=body, headers=headers, proxies=proxies)

    data = response.json()
    
    print(data)

    routes = list()

    for route in data["routes"]:
        coords = polyline.decode(route["geometry"])
        distance = route["summary"]["distance"]

        routes.append((coords, distance))

    return routes

def get_combined_bbox(routes, margin=0.0003):
    all_lats = []
    all_lons = []

    for route in routes:
        for lat, lon in route[0]:
            all_lats.append(lat)
            all_lons.append(lon)

    south = min(all_lats) - margin
    north = max(all_lats) + margin
    west = min(all_lons) - margin
    east = max(all_lons) + margin

    return south, west, north, east


def overpass_corridor(routes):

    sampled_points = []

    for route in routes:
        sampled_points.extend(route[0][::7])

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

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query},
        proxies=proxies
    )

    print("Status:", response.status_code)

    return response.json()


def parse_osm(osm_data):

    street_lamps = []
    roads = []

    for el in osm_data["elements"]:

        if el["type"] == "node":
            tags = el.get("tags", {})
            if tags.get("highway") == "street_lamp":
                street_lamps.append(el)

        elif el["type"] == "way":
            roads.append(el)

    return roads, street_lamps


def calculate_route_risk(route_coords, roads, lamps):

    route_line = LineString([(lon, lat) for lat, lon in route_coords])

    risk = 0

    for way in roads:
        if "geometry" not in way:
            continue

        coords = [(pt["lon"], pt["lat"]) for pt in way["geometry"]]
        way_line = LineString(coords)

        if route_line.distance(way_line) > 0.00015:
            continue

        tags = way.get("tags", {})
        highway = tags.get("highway")
        lit = tags.get("lit")
        access = tags.get("access")

        if highway == "primary":
            risk += 3
        elif highway == "tertiary":
            risk += 2

        if lit == "no":
            risk += 3
        elif lit is None:
            risk += 1

        if access == "private":
            risk += 2

    for lamp in lamps:
        point = Point(lamp["lon"], lamp["lat"])
        if route_line.distance(point) < 0.00015:
            risk -= 0.5

    return risk

def comment_of_ai(routes, roads, lamps, ind):

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "SecurityRouteApp"
    }


    prompt = f"""Представь - ты персонаж моей программы, который дает комментарии пользователю. Моя программа оценивает безопасность пешеходных маршрутов на основе данных OpenStreetMap. Она анализирует типы дорог, наличие освещения и количество уличных фонарей вдоль маршрута. Программа говорит, что самым безопасным является маршрут {ind+1}.
        Пожалуйста, дай НЕБОЛЬШОЙ комментарий с точки зрения безопасности. (Не указывай номер маршрута, говори ЭТОТ).
        Исходные данные: маршруты {routes}, дороги {roads}, фонари {lamps}.
        Ответ дай СТРОГО в JSON-ФОРМАТЕ!
    """

    data = {
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, proxies=proxies)
    resp = response.json()
    content = resp["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    comment = parsed["comment"]

    return comment

def get_safety_route(start_lat, start_lon, end_lat, end_lon):
    routes = get_route(start_lat, start_lon, end_lat, end_lon)
    
    data = overpass_corridor(routes)
    roads, lamps = parse_osm(data)


    risks = []
    distances = []
    for i, route in enumerate(routes):
        distances.append(route[1])
        r = calculate_route_risk(route[0], roads, lamps)
        risks.append(r)

    idx_min_risk = risks.index(min(risks))
    idx_min_distance = distances.index(min(distances))
    comment = comment_of_ai(routes, roads, lamps, idx_min_risk)

    return routes[idx_min_risk], routes[idx_min_distance], comment

