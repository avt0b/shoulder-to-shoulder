import logging

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


class HttpServiceClient:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        self.is_connected = False

    async def connect(self) -> bool:
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(settings.http_timeout))
        self.is_connected = True
        logger.info("HTTP client initialized")
        return True

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()
        self.client = None
        self.is_connected = False
        logger.info("HTTP client closed")

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        content: bytes | None = None,
    ) -> httpx.Response:
        if not self.client or not self.is_connected:
            raise RuntimeError("HTTP client is not initialized")

        return await self.client.request(
            method=method,
            url=url,
            headers=headers,
            content=content,
        )


http_client = HttpServiceClient()
