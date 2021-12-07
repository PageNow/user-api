import os
import sys
import logging
from logging.config import fileConfig

import alembic
from sqlalchemy import engine_from_config, create_engine, pool
from psycopg2 import DatabaseError

# we're appending the app directory to our path here
# so that we can import config easily
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# need to import models for alembic to include in its commit
import app.models.user
import app.models.friendship
import app.models.share_notification
import app.models.share_notification_seen

from app.core.config import DATABASE_URL, POSTGRES_DB
from app.db.db import metadata


# Alembic Config object, which provides access to values within the .ini file
config = alembic.context.config

# Interpret the config file for logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

target_metadata = metadata


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode
    """

    # handle testing config for migrations
    if os.environ.get("TESTING"):
        # connect to primary db
        default_engine = create_engine(
            str(DATABASE_URL), isolation_level="AUTOCOMMIT"
        )
        # drop testing db if it exists and create a fresh one
        with default_engine.connect() as default_conn:
            default_conn.execute(f"DROP DATABASE IF EXISTS {POSTGRES_DB}_test")
            default_conn.execute(f"CREATE DATABASE {POSTGRES_DB}_test")

    connectable = config.attributes.get("connection", None)
    config.set_main_option("sqlalchemy.url", str(DATABASE_URL))
    if connectable is None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        alembic.context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with alembic.context.begin_transaction():
            alembic.context.run_migrations()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """

    if os.environ.get("TESTING"):
        raise DatabaseError(
            "Running testing migrations offline currently not permitted."
        )

    alembic.context.configure(
        url=str(DATABASE_URL),
        target_metadata=target_metadata,
        dialect_opts={"paramstyle": "named"},
    )
    with alembic.context.begin_transaction():
        alembic.context.run_migrations()


if alembic.context.is_offline_mode():
    logger.info("Running migrations offline")
    run_migrations_offline()
else:
    logger.info("Running migrations online")
    run_migrations_online()
