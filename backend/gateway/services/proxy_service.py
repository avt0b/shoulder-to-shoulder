from urllib.parse import urljoin

import httpx
from fastapi import HTTPException, Request, status
from starlette.responses import Response

from ..config import settings
from ..core.http_client import http_client
from ..repositories.service_registry import ServiceRegistry

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}

RESPONSE_HEADERS = {
    "content-type",
    "content-disposition",
    "cache-control",
    "etag",
    "last-modified",
}


class ProxyService:
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry

    async def forward(self, request: Request, path: str) -> Response:
        self._validate_path(path)
        target = self.registry.resolve(path)
        upstream_url = self._build_upstream_url(target.base_url, path, request)
        headers = self._build_upstream_headers(request)
        body = await request.body()

        try:
            upstream_response = await http_client.request(
                request.method,
                upstream_url,
                headers=headers,
                content=body if body else None,
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=f"{target.name} timed out",
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"{target.name} unavailable: {exc}",
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=self._build_response_headers(upstream_response),
            media_type=upstream_response.headers.get("content-type"),
        )

    def _validate_path(self, path: str) -> None:
        if "\\" in path or any(segment in {".", ".."} for segment in path.split("/")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid proxy path",
            )

    def _build_upstream_url(self, base_url: str, path: str, request: Request) -> str:
        upstream_path = f"{settings.api_v1_prefix}/{path}".replace("//", "/")
        url = urljoin(f"{base_url.rstrip('/')}/", upstream_path.lstrip("/"))
        if request.url.query:
            return f"{url}?{request.url.query}"
        return url

    def _build_upstream_headers(self, request: Request) -> dict[str, str]:
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in HOP_BY_HOP_HEADERS
        }
        headers["x-forwarded-host"] = request.headers.get("host", "")
        headers["x-forwarded-proto"] = request.url.scheme
        return headers

    def _build_response_headers(self, response: httpx.Response) -> dict[str, str]:
        return {
            key: value
            for key, value in response.headers.items()
            if key.lower() in RESPONSE_HEADERS
        }
