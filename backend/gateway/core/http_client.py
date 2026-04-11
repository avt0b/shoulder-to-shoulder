import asyncio
import logging
from typing import Optional, Dict, Any

import aiohttp

from ..config import settings

logger = logging.getLogger(__name__)


class HttpServiceClient:
    """HTTP client for microservice communication using aiohttp.
    
    Singleton pattern to maintain single aiohttp.ClientSession throughout
    the application lifetime.
    """
    
    _instance: Optional['HttpServiceClient'] = None
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected: bool = False
    
    @classmethod
    def get_instance(cls) -> 'HttpServiceClient':
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    async def connect(self) -> bool:
        """Initialize aiohttp ClientSession."""
        try:
            timeout = aiohttp.ClientTimeout(total=settings.http_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            self.is_connected = True
            logger.info("✓ HTTP client initialized (aiohttp)")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to initialize HTTP client: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close aiohttp ClientSession."""
        if self.session:
            await self.session.close()
            self.is_connected = False
            logger.info("✓ HTTP client closed")
    
    async def _request(
        self, 
        method: str, 
        url: str, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Generic request handler with error handling and logging."""
        if not self.session or not self.is_connected:
            logger.error("HTTP client not initialized or disconnected")
            return None
        
        try:
            logger.debug(f"{method} {url} with params: {kwargs}")
            
            async with self.session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                logger.debug(f"Response status: {response.status}")
                
                # Handle all 2xx responses as success
                if 200 <= response.status < 300:
                    try:
                        return await response.json()
                    except Exception as e:
                        logger.warning(f"Failed to parse JSON response: {e}")
                        return {"status": response.status, "raw": response_text}
                
                # Log error responses with their content
                logger.error(
                    f"❌ {method} {url} returned {response.status}: {response_text}"
                )
                return response_text
                
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout on {method} {url}")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"❌ Client error on {method} {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error on {method} {url}: {e}")
            return None
    
    async def get(
        self, 
        url: str, 
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """GET request."""
        return await self._request("GET", url, params=params, headers=headers)
    
    async def post(
        self, 
        url: str, 
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """POST request with JSON payload."""
        print(json)
        print(data)
        if json is not None:
            return await self._request("POST", url, json=json, headers=headers)
        elif data is not None:
            return await self._request("POST", url, data=data, headers=headers)
        return await self._request("POST", url, headers=headers)
    
    async def put(
        self, 
        url: str, 
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """PUT request with JSON payload."""
        return await self._request("PUT", url, json=json, headers=headers)
    
    async def delete(
        self, 
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Optional[Dict[str, Any]]:
        """DELETE request."""
        return await self._request("DELETE", url, headers=headers)


http_client = HttpServiceClient()
