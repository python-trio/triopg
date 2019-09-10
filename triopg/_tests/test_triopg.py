import pytest
import trio_asyncio

import triopg


async def execute_queries(triopg_conn, asyncpg_conn):
    @trio_asyncio.aio_as_trio
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

    assert await triopg_conn.fetchval("""SELECT 1""") == 1
    assert list(await triopg_conn.fetchrow("""VALUES (0, 1, 2, 3)""")) == list(
        range(4)
    )

    user_ids = [(str(i),) for i in range(2, 11)]
    await triopg_conn.executemany(
        """INSERT INTO users (user_id) VALUES ($1)""", user_ids
    )

    assert await _asyncpg_query("""SELECT * FROM users""") == "SELECT 10"


@pytest.mark.trio
async def test_triopg_connection(
        asyncio_loop, asyncpg_conn, postgresql_connection_specs
):
    async with triopg.connect(**postgresql_connection_specs) as conn:
        await execute_queries(conn, asyncpg_conn)

    with pytest.raises(triopg.InterfaceError):
        await conn.execute("SELECT * FROM users")


@pytest.mark.trio
async def test_triopg_pool(
        asyncio_loop, asyncpg_conn, postgresql_connection_specs
):
    async with triopg.create_pool(**postgresql_connection_specs) as pool:
        async with pool.acquire() as conn:
            await execute_queries(conn, asyncpg_conn)
        await execute_queries(conn, asyncpg_conn)

    with pytest.raises(triopg.InterfaceError):
        async with pool.acquire() as conn:
            pass
