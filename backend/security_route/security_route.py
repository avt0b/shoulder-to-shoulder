import requests

def get_route(start_lat, start_lon, end_lat, end_lon):
    url = (
        f"https://router.project-osrm.org/route/v1/foot/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full&geometries=polyline"
    )

    response = requests.get(url)
    data = response.json()

    if data["code"] != "Ok":
        raise Exception("Ошибка при получении маршрута")

    route = list()
    for point in data["waypoints"]:
        temp = [point["location"][1], point["location"][0]]
        route.append(temp)
        
    distance = data["routes"][0]["distance"]

    return route, distance


def check_safety(lat, lon):
    query = f"""
    [out:json];
    way(around:10,{lat},{lon});
    out body;
    """

    response = requests.post(
        "https://overpass-api.de/api/interpreter",
        data={"data": query}
    )

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

    total_score = 0

    for lat, lon in route:
        total_score += check_safety(lat, lon)

    return {
        "route": route,
        "distance_meters": distance,
        "safety_score": total_score
    }

if __name__ == "__main__":
    ans = evaluate_route(52.974914, 36.051040, 52.971851, 36.057492)
    print(ans)