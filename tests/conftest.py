import asyncio
import os
import asyncpg
import pytest

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]


@pytest.fixture(scope="session")
def event_loop():
    """Override event_loop fixture because default scope is function."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
@pytest.fixture(scope="session")
async def db_conn():
    dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
    conn = await asyncpg.connect(dsn)
    yield conn
    await conn.close()


@pytest.mark.asyncio
@pytest.fixture(scope="class")
async def init_db(db_conn):
    async def truncate(db_conn):
        query = "TRUNCATE TABLE tasks RESTART IDENTITY"
        await db_conn.execute(query)

    async def insert_dummy(db_conn):
        records = [
            ['title1', 'content1', 'shun'],
            ['title2', '', 'shun'],
            ['title3', None, 'shun'],
            ['title4', 'content4', 'dummyuser'],
            ['title5', '', 'dummyuser'],
            ['title6', None, 'dummyuser'],
        ]
        query = "INSERT INTO tasks (title, content, username) VALUES($1, $2, $3)"
        await db_conn.executemany(query, records)

    await truncate(db_conn)
    await insert_dummy(db_conn)
