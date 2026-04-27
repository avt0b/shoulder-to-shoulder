from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ....utils.nats_client import NatsRpcClient

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=dict)
async def get_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    host_id: Optional[str] = Query(None),
    spot_id: Optional[str] = Query(None),
):
    """Получить список событий из event_service"""
    nats_client = NatsRpcClient.get_instance()
    
    if not nats_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"error": "Event service недоступен (NATS не подключен)"}
        )
    
    events = await nats_client.get_event_list(
        limit=limit,
        offset=offset,
        status=status,
        host_id=host_id,
        spot_id=spot_id
    )
    
    if events is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "Event service временно недоступен"}
        )
    
    return {"events": events, "limit": limit, "offset": offset}


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    """Получить детальную информацию о событии"""
    nats_client = NatsRpcClient.get_instance()
    
    if not nats_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"error": "Event service недоступен (NATS не подключен)"}
        )
    
    event = await nats_client.get_event(event_id)
    
    if event is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Событие не найдено или event service недоступен"}
        )
    
    return {"event": event}


@router.delete("/{event_id}", response_model=dict)
async def delete_event(event_id: str):
    """Удалить событие"""
    nats_client = NatsRpcClient.get_instance()
    
    if not nats_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"error": "Event service недоступен (NATS не подключен)"}
        )
    
    success = await nats_client.delete_event(event_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail={"error": "Не удалось удалить событие"}
        )
    
    return {"success": True, "message": "Событие удалено"}


@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, **fields):
    """Обновить событие"""
    nats_client = NatsRpcClient.get_instance()
    
    if not nats_client.is_connected:
        raise HTTPException(
            status_code=503,
            detail={"error": "Event service недоступен (NATS не подключен)"}
        )
    
    updated_event = await nats_client.update_event(event_id, **fields)
    
    if updated_event is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "Не удалось обновить событие"}
        )
    
    return {"event": updated_event}
