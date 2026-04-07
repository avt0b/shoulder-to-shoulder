import os
import sys
from pathlib import Path
from dotenv import load_dotenv

root_path = str(Path(__file__).parents[3])
if root_path not in sys.path:
    sys.path.insert(0, root_path)

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from backend.user_service.app.core.database import Base
from backend.user_service.app.domain.models.user import User
from backend.user_service.app.domain.models.profile import UserProfile
from backend.user_service.app.domain.models.rating import UserRating
from backend.user_service.app.domain.models.badge import Badge


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()