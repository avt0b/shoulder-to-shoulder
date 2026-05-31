from fastapi import APIRouter, Depends, Request
from starlette.responses import Response

from ....core.security import validate_gateway_request
from ....repositories.service_registry import ServiceRegistry
from ....services.proxy_service import ProxyService

router = APIRouter(tags=["proxy"])

registry = ServiceRegistry()
proxy_service = ProxyService(registry)


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy(path: str, request: Request, _=Depends(validate_gateway_request)) -> Response:
    return await proxy_service.forward(request, path)
