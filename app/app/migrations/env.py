"""
Alembic migration environment setup.

This file configures Alembic's runtime environment and
handles running migrations in both offline and online modes.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# pylint: disable=no-member
from alembic import context
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.dev")
load_dotenv(dotenv_path=".env.secret")

# pylint: disable=wrong-import-position
# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
from models import *
# pylint: enable=wildcard-import
from db import Base
from core import settings

# pylint: enable=wrong-import-position

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option('sqlalchemy.url', str(settings.POSTGRES_DATABASE_URI))


def render_item(type_, obj, autogen_context):  # pylint: disable=unused-argument
    """Custom render function to support user-defined types like RulesType."""
    if isinstance(obj, RulesType):
        autogen_context.imports.add("from models import RulesType")
        return "RulesType(length=sa.TEXT())"
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations in 'online' mode."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
