import json
import logging
from typing import Optional, Dict, Any
from nats.errors import TimeoutError, NoRespondersError
from nats.aio.client import Client as NATS

logger = logging.getLogger(__name__)


class NatsRpcClient:
    """NATS RPC клиент для общения между микросервисами"""
    
    _instance: Optional['NatsRpcClient'] = None
    
    def __init__(self):
        self.nc: Optional[NATS] = None
        self.timeout = 5.0  # секунды на каждый запрос
        self.is_connected = False
    
    @classmethod
    def get_instance(cls) -> 'NatsRpcClient':
        """Singleton паттерн"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect(self, server: str = "nats://localhost:4222") -> bool:
        """Подключиться к NATS"""
        try:
            self.nc = NATS()
            await self.nc.connect(server)
            self.is_connected = True
            logger.info(f"✓ Подключено к NATS на {server}")
            return True
        except Exception as e:
            logger.error(f"✗ Ошибка подключения к NATS: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Отключиться от NATS"""
        if self.nc:
            await self.nc.close()
            self.is_connected = False
            logger.info("✓ Отключено от NATS")
    
    async def _request(self, subject: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Отправить Request/Reply с обработкой ошибок"""
        if not self.is_connected or not self.nc:
            logger.error(f"✗ NATS не подключен")
            return None
        
        try:
            msg = await self.nc.request(
                subject,
                json.dumps(payload).encode(),
                timeout=self.timeout
            )
            response = json.loads(msg.data.decode())
            return response
        except TimeoutError:
            logger.warning(f"⏱️ Timeout на {subject} (>{self.timeout}s)")
            return None
        except NoRespondersError:
            logger.warning(f"🚫 Нет ответчика для {subject}")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка на {subject}: {e}")
            return None
    
    # ===== FORUM SERVICE (MEETUPS) =====
    
    async def get_user_meetups(self, user_id: int) -> Optional[list]:
        """Получить мероприятия пользователя из forum_service"""
        result = await self._request("forum.meetup.user.list", {"user_id": user_id})
        return result.get("meetups", []) if result else []
    
    async def get_meetup_details(self, meetup_id: int) -> Optional[Dict[str, Any]]:
        """Получить детали мероприятия из forum_service"""
        result = await self._request("forum.meetup.get", {"meetup_id": meetup_id})
        return result.get("data") if result else None
    
    async def join_meetup(self, meetup_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Присоединиться к мероприятию"""
        result = await self._request(
            "forum.meetup.join",
            {"meetup_id": meetup_id, "user_id": user_id}
        )
        return result
    
    async def leave_meetup(self, meetup_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Покинуть мероприятие"""
        result = await self._request(
            "forum.meetup.leave",
            {"meetup_id": meetup_id, "user_id": user_id}
        )
        return result
    
    async def search_meetups_by_location(self, lat: float, lng: float, radius_m: int = 2000) -> Optional[list]:
        """Найти мероприятия по координатам в forum_service"""
        result = await self._request(
            "forum.meetup.search",
            {"lat": lat, "lng": lng, "radius_m": radius_m}
        )
        return result.get("meetups", []) if result else []
    
    # ===== USER SERVICE =====
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить профиль пользователя из user_service"""
        result = await self._request("user.profile.get", {"user_id": user_id})
        return result.get("data") if result else None
    
    # ===== EVENT SERVICE =====

    async def get_event_list(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        host_id: Optional[str] = None,
        spot_id: Optional[str] = None
    ) -> Optional[list]:
        """Получить список событий из event_service"""
        payload = {
            "limit": limit,
            "offset": offset,
            "status": status,
            "host_id": host_id,
            "spot_id": spot_id
        }
        result = await self._request("admin.event.list", payload)
        return result.get("data", []) if result and result.get("ok") else None

    async def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Получить детальную информацию о событии"""
        result = await self._request("admin.event.get", {"event_id": event_id})
        return result.get("data") if result and result.get("ok") else None

    async def delete_event(self, event_id: str) -> bool:
        """Удалить событие"""
        result = await self._request("admin.event.delete", {"event_id": event_id})
        return bool(result and result.get("ok"))

    async def update_event(self, event_id: str, **fields) -> Optional[Dict[str, Any]]:
        """Обновить событие"""
        payload = {"event_id": event_id, **fields}
        result = await self._request("admin.event.update", payload)
        return result.get("data") if result and result.get("ok") else None