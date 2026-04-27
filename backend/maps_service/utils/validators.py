from typing import Tuple


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Валидировать координаты.
    
    Args:
        latitude: широта (-90 до 90)
        longitude: долгота (-180 до 180)
    
    Returns:
        True если координаты валидны, иначе False
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_distance(distance_km: float) -> bool:
    """Валидировать расстояние в км"""
    return 0.1 <= distance_km <= 50.0


def validate_rating(rating: float) -> bool:
    """Валидировать рейтинг (0-5)"""
    return 0.0 <= rating <= 5.0


def validate_activity_type(activity_type: str) -> bool:
    """Валидировать тип активности"""
    valid_types = [
        "workout", "horizontal_bar", "stretching", "running",
        "basketball", "volleyball", "tennis", "football"
    ]
    return activity_type in valid_types


def validate_noise_level(noise_level: str) -> bool:
    """Валидировать уровень шума"""
    valid_levels = ["quiet", "moderate", "loud"]
    return noise_level in valid_levels
