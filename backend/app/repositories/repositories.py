import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from sqlalchemy import func, select
from app.models import Team, Flag, Submission


class TeamRepository:
    """Репозиторий для работы с командами (Teams)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, team_id: uuid.UUID) -> Team | None:
        """Получить команду по ID"""
        query = select(Team).where(Team.id == team_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_name(self, name: str) -> Team | None:
        """Получить команду по названию"""
        query = select(Team).where(Team.name == name)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self) -> list[Team]:
        query = select(Team).order_by(Team.score.desc(), Team.created_at.asc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, name: str, password_hash: str) -> Team:
        """Создать новую команду"""
        team = Team(name=name, password_hash=password_hash)
        self.session.add(team)
        await self.session.flush()
        await self.session.commit()
        return team

    async def update_score(self, team_id: uuid.UUID, points: int) -> Team | None:
        """Обновить очки команды"""
        team = await self.get_by_id(team_id)
        if team:
            team.score += points
            await self.session.flush()
        return team

    async def get_all_with_rank(self) -> list[dict]:
        """Получить все команды с рангом"""
        query = select(Team).order_by(Team.score.desc())
        result = await self.session.execute(query)
        teams = result.scalars().all()

        return [
            {
                "id": team.id,
                "name": team.name,
                "score": team.score,
                "rank": idx + 1,
            }
            for idx, team in enumerate(teams)
        ]

    async def set_ban(
        self,
        team_id: uuid.UUID,
        is_banned: bool,
        reason: str | None = None,
    ) -> Team | None:
        team = await self.get_by_id(team_id)
        if not team:
            return None

        team.is_banned = is_banned
        team.ban_reason = reason if is_banned else None
        team.banned_at = datetime.utcnow() if is_banned else None
        await self.session.flush()
        return team


class FlagRepository:
    """Репозиторий для работы с флагами (Flags)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_flag_text(self, flag_text: str) -> Flag | None:
        """Получить флаг по текст"""
        query = select(Flag).where(Flag.flag == flag_text)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_id(self, flag_id: uuid.UUID) -> Flag | None:
        """Получить флаг по ID"""
        query = select(Flag).where(Flag.id == flag_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create(self, flag_text: str, points: int, description: str = None) -> Flag:
        """Создать новый флаг"""
        flag = Flag(flag=flag_text, points=points, description=description)
        self.session.add(flag)
        await self.session.flush()
        return flag

    async def delete(self, flag_id: uuid.UUID) -> bool:
        flag = await self.get_by_id(flag_id)
        if not flag:
            return False
        await self.session.delete(flag)
        await self.session.flush()
        return True

    async def get_all(self) -> list[Flag]:
        """Получить все флаги"""
        query = select(Flag).order_by(Flag.created_at.desc())
        result = await self.session.execute(query)
        return result.scalars().all()


class SubmissionRepository:
    """Репозиторий для работы с попытками (Submissions)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        team_id: uuid.UUID,
        flag_text: str,
        flag_id: uuid.UUID | None = None,
        correct: bool = False,
    ) -> Submission:
        """Создать новую попытку"""
        submission = Submission(
            team_id=team_id,
            flag_text=flag_text,
            flag_id=flag_id,
            correct=correct,
        )
        self.session.add(submission)
        await self.session.flush()
        return submission

    async def get_by_team(self, team_id: uuid.UUID) -> list[Submission]:
        """Получить все попытки команды"""
        query = (
            select(Submission)
            .where(Submission.team_id == team_id)
            .order_by(Submission.created_at.desc())
            .limit(50)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recent(self, limit: int = 100) -> list[Submission]:
        query = (
            select(Submission)
            .order_by(Submission.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_by_team(self, team_id: uuid.UUID, correct: bool | None = None) -> int:
        query = select(func.count(Submission.id)).where(Submission.team_id == team_id)
        if correct is not None:
            query = query.where(Submission.correct.is_(correct))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count_by_flag(self, flag_id: uuid.UUID, correct: bool | None = None) -> int:
        query = select(func.count(Submission.id)).where(Submission.flag_id == flag_id)
        if correct is not None:
            query = query.where(Submission.correct.is_(correct))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def count(self, correct: bool | None = None) -> int:
        query = select(func.count(Submission.id))
        if correct is not None:
            query = query.where(Submission.correct.is_(correct))
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_correct_for_team(self, team_id: uuid.UUID) -> list[Submission]:
        """Получить все правильные попытки команды"""
        query = (
            select(Submission)
            .where(Submission.team_id == team_id, Submission.correct.is_(True))
            .order_by(Submission.created_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def team_already_solved(
        self, team_id: uuid.UUID, flag_id: uuid.UUID
    ) -> bool:
        """Проверить, решила ли команда этот флаг"""
        query = (
            select(func.count(Submission.id))
            .where(
                Submission.team_id == team_id,
                Submission.flag_id == flag_id,
                Submission.correct.is_(True),
            )
        )
        result = await self.session.execute(query)
        count = result.scalar()
        return count > 0
