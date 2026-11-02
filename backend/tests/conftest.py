"""Pytest fixtures for MediDesk backend tests.

Every test runs inside a transaction that is rolled back after the test,
so nothing a test writes is ever committed.
"""
import sys
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection
from psycopg.rows import dict_row

from app.config import settings
from app.db import get_db
from app.main import app


class MockCursor:
    def __init__(self, data=None):
        self.data = data or []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def execute(self, query, params=None):
        pass

    async def fetchall(self):
        return self.data

    async def fetchone(self):
        return self.data[0] if self.data else None


class MockConnection:
    def __init__(self):
        self.rolled_back = False

    async def execute(self, query, params=None):
        if "SELECT DISTINCT category" in query:
            return MockCursor([{"category": "Antibiotic"}, {"category": "Painkiller"}])
        return MockCursor([{"?column?": 1}])

    async def commit(self):
        pass

    async def rollback(self):
        self.rolled_back = True

    async def close(self):
        pass


@pytest_asyncio.fixture()
async def db_conn() -> AsyncGenerator[object, None]:
    """Provide a real database connection wrapped in an isolated transaction that rolls back."""
    target_dsn = settings.DATABASE_URL
    conn = await AsyncConnection.connect(
        target_dsn, row_factory=dict_row, autocommit=False
    )
    try:
        yield conn
    finally:
        await conn.rollback()
        await conn.close()


@pytest_asyncio.fixture()
async def client(db_conn: object) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client using the transaction connection (rolled back per test)."""

    async def _override_get_db():
        yield db_conn

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
