import requests

proxies = {
    "http": "socks5h://127.0.0.1:12334",
    "https": "socks5h://127.0.0.1:12334",
}

def get_route(start_lat, start_lon, end_lat, end_lon):
    url = (
        f"https://router.project-osrm.org/route/v1/foot/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full&geometries=polyline"
    )

    response = requests.get(url, proxies=proxies)
    data = response.json()

    if data["code"] != "Ok":
        raise Exception("Ошибка при получении маршрута")

    route = list()
    for point in data["waypoints"]:
        temp = [point["location"][1], point["location"][0]]
        route.append(temp)
        
    distance = data["routes"][0]["distance"]

    return route, distance


def check_safety(points):
    url = (
        f'https://overpass-api.de/api/interpreter?data=[out:json];('
    )

    for point in points: 
        url += f'way(around:5,{point [0]},{point[1]})["highway"];'

    url += ')["lit"];out%20body;'

    response = requests.get(url, proxies=proxies)

    data = response.json()
    score = 0

    for element in data.get("elements", []):
        tags = element.get("tags", {})

        # Освещённость
        if tags.get("lit") == "yes":
            score += 2
        else:
            score -= 1

        # Тротуар
        if tags.get("sidewalk") == "yes":
            score += 2

        # Тип дороги
        if tags.get("highway") in ["primary", "trunk"]:
            score -= 3

    return score


def evaluate_route(start_lat, start_lon, end_lat, end_lon):
    route, distance = get_route(start_lat, start_lon, end_lat, end_lon)

#    total_score = check_safety(route)

    return {
        "route": route,
        "distance_meters": distance,
#        "safety_score": total_score
    }

def get_safety_route(start_lat, start_lon, end_lat, end_lon):
    ans = evaluate_route(start_lat, start_lon, end_lat, end_lon)
    return ans
