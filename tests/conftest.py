import pytest
import warnings
import os

from fastapi.applications import FastAPI
from httpx import AsyncClient
import alembic
from alembic.config import Config
from databases import Database


# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = True
    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


# Create a new application for testing
@pytest.fixture(scope="module")
def test_app() -> FastAPI:
    from app.main import app

    return app


# Grab a reference to our database when needed
@pytest.fixture
def db(test_app: FastAPI) -> Database:
    return test_app.state._db


@pytest.fixture()
async def client(test_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=test_app,
        base_url="http://test"
    ) as client:
        yield client
