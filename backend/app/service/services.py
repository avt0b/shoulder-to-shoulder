import hashlib
import uuid
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories import FlagRepository, SubmissionRepository, TeamRepository
from app.schemas import (
    AdminAnalyticsResponse,
    AdminFlagCreateRequest,
    AdminFlagResponse,
    AdminSubmissionResponse,
    AdminTeamResponse,
    ScoreboardEntry,
    SubmissionResponse,
    SubmitFlagResponse,
    TeamTaskResponse,
    TeamResponse,
)


def _password_bytes(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("ascii")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session)

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("ascii")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        hashed_bytes = hashed_password.encode("ascii")
        if bcrypt.checkpw(_password_bytes(plain_password), hashed_bytes):
            return True

        # Backward compatibility for existing plain bcrypt hashes.
        plain_bytes = plain_password.encode("utf-8")
        if len(plain_bytes) <= 72:
            return bcrypt.checkpw(plain_bytes, hashed_bytes)

        return False

    def create_access_token(
        self,
        team_id: uuid.UUID,
        expires_delta: timedelta | None = None,
    ) -> str:
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

        payload = {
            "sub": str(team_id),
            "exp": datetime.utcnow() + expires_delta,
            "type": "access",
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> uuid.UUID | None:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            team_id = payload.get("sub")
            if team_id is None:
                return None
            return uuid.UUID(team_id)
        except (JWTError, ValueError):
            return None

    async def login(self, team_name: str, password: str) -> dict[str, str] | None:
        team = await self.team_repo.get_by_name(team_name)
        if not team or team.is_banned or not self.verify_password(password, team.password_hash):
            return None

        token = self.create_access_token(team.id)
        return {"access_token": token, "token_type": "bearer"}

    async def register(self, team_name: str, password: str) -> dict[str, str] | None:
        existing_team = await self.team_repo.get_by_name(team_name)
        if existing_team:
            return None

        password_hash = self.hash_password(password)
        team = await self.team_repo.create(name=team_name, password_hash=password_hash)
        token = self.create_access_token(team.id)
        return {"access_token": token, "token_type": "bearer"}


class TeamService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session)

    async def get_team_with_rank(self, team_id: uuid.UUID) -> TeamResponse | None:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            return None

        all_teams = await self.team_repo.get_all_with_rank()
        rank = next(
            (t["rank"] for t in all_teams if t["id"] == team_id),
            len(all_teams) + 1,
        )
        return TeamResponse(id=team.id, name=team.name, score=team.score, rank=rank)


class FlagService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.flag_repo = FlagRepository(session)
        self.submission_repo = SubmissionRepository(session)
        self.team_repo = TeamRepository(session)

    async def submit_flag(self, team_id: uuid.UUID, flag_text: str) -> SubmitFlagResponse:
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            return SubmitFlagResponse(
                success=False,
                message="Team not found",
                points=None,
            )

        if team.is_banned:
            return SubmitFlagResponse(
                success=False,
                message="Team is banned",
                points=None,
            )

        flag = await self.flag_repo.get_by_flag_text(flag_text)

        if not flag:
            await self.submission_repo.create(
                team_id=team_id,
                flag_text=flag_text,
                flag_id=None,
                correct=False,
            )
            await self.session.commit()
            return SubmitFlagResponse(
                success=False,
                message="Wrong flag",
                points=None,
            )

        already_solved = await self.submission_repo.team_already_solved(team_id, flag.id)
        if already_solved:
            await self.submission_repo.create(
                team_id=team_id,
                flag_text=flag_text,
                flag_id=flag.id,
                correct=False,
            )
            await self.session.commit()
            return SubmitFlagResponse(
                success=False,
                message="Challenge already solved",
                points=None,
            )

        await self.submission_repo.create(
            team_id=team_id,
            flag_text=flag_text,
            flag_id=flag.id,
            correct=True,
        )
        await self.team_repo.update_score(team_id, flag.points)
        await self.session.commit()

        return SubmitFlagResponse(
            success=True,
            message="Correct flag",
            points=flag.points,
        )

    async def get_team_submissions(self, team_id: uuid.UUID) -> list[SubmissionResponse]:
        submissions = await self.submission_repo.get_by_team(team_id)
        return [
            SubmissionResponse(
                id=submission.id,
                flag=submission.flag_text,
                correct=submission.correct,
                created_at=submission.created_at,
            )
            for submission in submissions
        ]

    async def get_team_tasks(self, team_id: uuid.UUID) -> list[TeamTaskResponse]:
        flags = await self.flag_repo.get_all()
        correct_submissions = await self.submission_repo.get_correct_for_team(team_id)
        solved_by_flag_id = {
            submission.flag_id: submission.created_at
            for submission in correct_submissions
            if submission.flag_id is not None
        }

        return [
            TeamTaskResponse(
                id=flag.id,
                description=flag.description,
                points=flag.points,
                solved=flag.id in solved_by_flag_id,
                solved_at=solved_by_flag_id.get(flag.id),
                created_at=flag.created_at,
            )
            for flag in flags
        ]


class ScoreboardService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session)

    async def get_scoreboard(self) -> list[ScoreboardEntry]:
        teams_with_rank = await self.team_repo.get_all_with_rank()
        return [
            ScoreboardEntry(
                rank=team["rank"],
                team_name=team["name"],
                score=team["score"],
            )
            for team in teams_with_rank
        ]


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.team_repo = TeamRepository(session)
        self.flag_repo = FlagRepository(session)
        self.submission_repo = SubmissionRepository(session)

    async def create_flag(self, request: AdminFlagCreateRequest) -> AdminFlagResponse:
        existing_flag = await self.flag_repo.get_by_flag_text(request.flag)
        if existing_flag:
            raise ValueError("Flag already exists")

        flag = await self.flag_repo.create(
            flag_text=request.flag,
            points=request.points,
            description=request.description,
        )
        await self.session.commit()
        return AdminFlagResponse(
            id=flag.id,
            flag=flag.flag,
            description=flag.description,
            points=flag.points,
            created_at=flag.created_at,
            solves=0,
        )

    async def list_flags(self) -> list[AdminFlagResponse]:
        flags = await self.flag_repo.get_all()
        result = []
        for flag in flags:
            solves = await self.submission_repo.count_by_flag(flag.id, correct=True)
            result.append(
                AdminFlagResponse(
                    id=flag.id,
                    flag=flag.flag,
                    description=flag.description,
                    points=flag.points,
                    created_at=flag.created_at,
                    solves=solves,
                )
            )
        return result

    async def delete_flag(self, flag_id: uuid.UUID) -> bool:
        deleted = await self.flag_repo.delete(flag_id)
        await self.session.commit()
        return deleted

    async def list_teams(self) -> list[AdminTeamResponse]:
        teams = await self.team_repo.get_all()
        ranked = await self.team_repo.get_all_with_rank()
        ranks = {team["id"]: team["rank"] for team in ranked}

        result = []
        for team in teams:
            submissions_count = await self.submission_repo.count_by_team(team.id)
            solves_count = await self.submission_repo.count_by_team(team.id, correct=True)
            result.append(
                AdminTeamResponse(
                    id=team.id,
                    name=team.name,
                    score=team.score,
                    rank=ranks.get(team.id, 0),
                    is_banned=team.is_banned,
                    ban_reason=team.ban_reason,
                    banned_at=team.banned_at,
                    created_at=team.created_at,
                    submissions_count=submissions_count,
                    solves_count=solves_count,
                )
            )
        return result

    async def ban_team(
        self,
        team_id: uuid.UUID,
        reason: str | None = None,
    ) -> AdminTeamResponse | None:
        team = await self.team_repo.set_ban(team_id, True, reason)
        if not team:
            return None
        await self.session.commit()
        return (await self.list_teams_by_ids([team.id]))[0]

    async def unban_team(self, team_id: uuid.UUID) -> AdminTeamResponse | None:
        team = await self.team_repo.set_ban(team_id, False)
        if not team:
            return None
        await self.session.commit()
        return (await self.list_teams_by_ids([team.id]))[0]

    async def list_teams_by_ids(self, team_ids: list[uuid.UUID]) -> list[AdminTeamResponse]:
        teams = await self.list_teams()
        wanted = set(team_ids)
        return [team for team in teams if team.id in wanted]

    async def get_analytics(self) -> AdminAnalyticsResponse:
        teams = await self.team_repo.get_all()
        flags = await self.flag_repo.get_all()
        submissions_count = await self.submission_repo.count()
        correct_submissions_count = await self.submission_repo.count(correct=True)
        wrong_submissions_count = await self.submission_repo.count(correct=False)

        return AdminAnalyticsResponse(
            teams_count=len(teams),
            banned_teams_count=sum(1 for team in teams if team.is_banned),
            flags_count=len(flags),
            submissions_count=submissions_count,
            correct_submissions_count=correct_submissions_count,
            wrong_submissions_count=wrong_submissions_count,
            total_score=sum(team.score for team in teams),
        )

    async def get_recent_submissions(self) -> list[AdminSubmissionResponse]:
        submissions = await self.submission_repo.get_recent(100)
        result = []
        for submission in submissions:
            team = await self.team_repo.get_by_id(submission.team_id)
            result.append(
                AdminSubmissionResponse(
                    id=submission.id,
                    team_id=submission.team_id,
                    team_name=team.name if team else "Unknown team",
                    flag_id=submission.flag_id,
                    flag=submission.flag_text,
                    correct=submission.correct,
                    created_at=submission.created_at,
                )
            )
        return result
