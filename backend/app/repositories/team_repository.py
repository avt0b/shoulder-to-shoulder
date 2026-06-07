from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.team import Team


class TeamRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(
        self,
        name: str
    ) -> Team | None:

        query = (
            select(Team)
            .where(Team.name == name)
        )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        team_id
    ) -> Team | None:

        return await self.db.get(
            Team,
            team_id
        )

    async def update_score(
        self,
        team: Team,
        points: int
    ):

        team.score += points

        await self.db.commit()