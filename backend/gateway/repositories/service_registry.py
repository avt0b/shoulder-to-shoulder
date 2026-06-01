from dataclasses import dataclass

from fastapi import HTTPException, status

from ..config import settings


@dataclass(frozen=True)
class ServiceTarget:
    name: str
    base_url: str


class ServiceRegistry:
    def __init__(self):
        self._routes: dict[str, ServiceTarget] = {
            "auth": ServiceTarget("user_service", settings.user_service_url),
            "users": ServiceTarget("user_service", settings.user_service_url),
            "events": ServiceTarget("event_service", settings.event_service_url),
            "media": ServiceTarget("media_service", settings.media_service_url),
            "places": ServiceTarget("maps_service", settings.maps_service_url),
            "route": ServiceTarget("maps_service", settings.maps_service_url),
            "admin": ServiceTarget("admin_service", settings.admin_service_url),
            "notifications": ServiceTarget("notification_service", settings.notification_service_url),
        }

    def resolve(self, path: str) -> ServiceTarget:
        first_segment = path.strip("/").split("/", 1)[0]
        target = self._routes.get(first_segment)
        if not target:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No upstream service configured for path '{first_segment}'",
            )
        return target
