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


@pytest.mark.trio
async def test_triopg_connection(
        asyncio_loop, asyncpg_conn, postgresql_connection_specs
):
    conn = await triopg.connect(**postgresql_connection_specs)
    await execute_queries(conn, asyncpg_conn)
    await conn.close()

    with pytest.raises(triopg.InterfaceError):
        await conn.execute("SELECT * FROM users")


@pytest.mark.trio
async def test_triopg_pool(
        asyncio_loop, asyncpg_conn, postgresql_connection_specs
):
    pool = await triopg.create_pool(**postgresql_connection_specs)
    try:
        async with pool.acquire() as conn:
            await execute_queries(conn, asyncpg_conn)
    finally:
        await pool.close()

    with pytest.raises(triopg.InterfaceError):
        async with pool.acquire() as conn:
            pass


@pytest.mark.trio
async def test_triopg_pool_context_manager(
        asyncio_loop, asyncpg_conn, postgresql_connection_specs
):
    async with triopg.create_pool_cm(**postgresql_connection_specs) as pool:
        async with pool.acquire() as conn:
            await execute_queries(conn, asyncpg_conn)

    with pytest.raises(triopg.InterfaceError):
        async with pool.acquire() as conn:
            pass
