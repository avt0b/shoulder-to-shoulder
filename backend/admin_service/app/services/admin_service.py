from fastapi import HTTPException, status
from app.core.nats_client import request


class AdminService:

    async def list_users(self, limit: int, offset: int, search: str | None = None) -> list[dict]:
        try:
            resp = await request("admin.user.list", {"limit": limit, "offset": offset, "search": search})
            if not resp.get("ok"):
                raise HTTPException(status_code=400, detail=resp.get("error"))
            return resp["data"]
        except RuntimeError:
            raise HTTPException(status_code=503, detail="User service is temporarily unavailable")

    async def get_user(self, user_id: str) -> dict | None:
        try:
            resp = await request("admin.user.get", {"user_id": user_id})
            if not resp.get("ok"):
                return None
            return resp["data"]
        except RuntimeError:
            raise HTTPException(status_code=503, detail="User service is temporarily unavailable")

    async def ban_user(self, user_id: str, reason: str | None = None) -> bool:
        try:
            resp = await request("admin.user.ban", {"user_id": user_id, "reason": reason})
            if not resp.get("ok"):
                return False
            return True
        except RuntimeError:
            raise HTTPException(status_code=503, detail="User service is temporarily unavailable")

    async def unban_user(self, user_id: str, comment: str | None = None) -> bool:
        try:
            resp = await request("admin.user.unban", {"user_id": user_id, "comment": comment})
            if not resp.get("ok"):
                return False
            return True
        except RuntimeError:
            raise HTTPException(status_code=503, detail="User service is temporarily unavailable")

    async def award_badge(self, user_id: str, badge_type: str) -> bool | None:
        try:
            resp = await request("admin.user.award_badge", {"user_id": user_id, "badge_type": badge_type})
            if not resp.get("ok"):
                return None
            return resp["data"].get("awarded")
        except RuntimeError:
            raise HTTPException(status_code=503, detail="User service is temporarily unavailable")

    async def list_spots(self, status_filter: str | None = None) -> list[dict]:
        try:
            resp = await request("admin.spot.list", {"status": status_filter})
            if not resp.get("ok"):
                raise HTTPException(status_code=400, detail=resp.get("error"))
            return resp["data"]
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Spot service is temporarily unavailable")

    async def get_spot(self, spot_id: str) -> dict | None:
        try:
            resp = await request("admin.spot.get", {"spot_id": spot_id})
            if not resp.get("ok"):
                return None
            return resp["data"]
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Spot service is temporarily unavailable")

    async def moderate_spot(self, spot_id: str, action: str, reason: str | None = None,
                            notes: str | None = None) -> dict | None:
        try:
            resp = await request("admin.spot.moderate",
                                 {"spot_id": spot_id, "action": action, "reason": reason, "notes": notes})
            if not resp.get("ok"):
                return None
            return resp["data"]
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Spot service is temporarily unavailable")

    async def delete_spot(self, spot_id: str) -> bool:
        try:
            resp = await request("admin.spot.delete", {"spot_id": spot_id})
            if not resp.get("ok"):
                return False
            return True
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Spot service is temporarily unavailable")
