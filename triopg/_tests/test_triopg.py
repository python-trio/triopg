import pytest
import asyncpg
import trio_asyncio
from asyncpg.cluster import Cluster
import tempfile

import triopg


@pytest.fixture(autouse=True)
async def asyncio_loop():
    async with trio_asyncio.open_loop() as loop:
        yield loop


@pytest.fixture(scope='session')
def cluster():
    cluster_dir = tempfile.mkdtemp()
    cluster = Cluster(cluster_dir)

    cluster.init()
    try:
        cluster.start(port='dynamic')
        yield cluster
        cluster.stop()
    finally:
        cluster.destroy()


@pytest.fixture
def postgresql_connection_specs(cluster):
    return {'database': 'postgres', **cluster.get_connection_spec()}


@pytest.fixture()
async def asyncpg_conn(asyncio_loop, postgresql_connection_specs):
    @trio_asyncio.trio2aio
    async def _open_connection():
        return await asyncpg.connect(**postgresql_connection_specs)

    @trio_asyncio.trio2aio
    async def _close_connection(conn):
        await conn.close()

    conn = await _open_connection()
    try:
        yield conn
    finally:
        await _close_connection(conn)


@pytest.fixture()
async def triopg_conn(postgresql_connection_specs):
    conn = await triopg.connect(**postgresql_connection_specs)
    try:
        yield conn
    finally:
        await conn.close()


async def execute_queries(triopg_conn, asyncpg_conn):
    @trio_asyncio.trio2aio
    async def _asyncpg_query(sql):
        return await asyncpg_conn.execute(sql)

    # Execute without transaction
    await triopg_conn.execute(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE IF NOT EXISTS users (
            _id SERIAL PRIMARY KEY,
            user_id VARCHAR(32) UNIQUE
        )"""
    )
    assert await _asyncpg_query("""SELECT * FROM users""") == "SELECT 0"

    # Execute in transaction without exception
    async with triopg_conn.transaction():
        await triopg_conn.execute("INSERT INTO users (user_id) VALUES (1)")
    assert await _asyncpg_query("""SELECT * FROM users""") == "SELECT 1"

    # Execute in transaction raising exception, request shound not be executed
    with pytest.raises(Exception):
        async with triopg_conn.transaction():
            await triopg_conn.execute("INSERT INTO users (user_id) VALUES (2)")
            raise Exception()

    assert await _asyncpg_query("""SELECT * FROM users""") == "SELECT 1"


@pytest.mark.trio
async def test_triopg_connection(asyncpg_conn, postgresql_connection_specs):
    conn = await triopg.connect(**postgresql_connection_specs)
    await execute_queries(conn, asyncpg_conn)
    await conn.close()


@pytest.mark.trio
async def test_triopg_pool(asyncpg_conn, postgresql_connection_specs):
    pool = await triopg.create_pool(**postgresql_connection_specs)
    async with pool.acquire() as conn:
        async with pool.acquire() as conn2:
            assert conn != conn2
        await execute_queries(conn, asyncpg_conn)
    await pool.close()
