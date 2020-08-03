import pytest
import trio_asyncio
import asyncpg

import triopg


def unwrap(record):
    assert isinstance(record, asyncpg.Record)
    return tuple(record.values())


@pytest.mark.trio
async def test_connection_closed(asyncio_loop, postgresql_connection_specs):
    async with triopg.connect(**postgresql_connection_specs) as conn:
        pass
    with pytest.raises(triopg.InterfaceError):
        await conn.execute("VALUES (1)")


@pytest.mark.trio
async def test_cursor(triopg_conn):
    async with triopg_conn.transaction():
        cursor_factory = triopg_conn.cursor(
            "VALUES ($1, 1), ($2, 2), ($3, 3), ($4, 4), ($5, 5)", "1", "2",
            "3", "4", "5"
        )
        cursor = await cursor_factory

        row = await cursor.fetchrow()
        assert unwrap(row) == ("1", 1)
        advanced = await cursor.forward(1)
        assert advanced == 1
        fetched = await cursor.fetch(2)
        assert [unwrap(x) for x in fetched] == [("3", 3), ("4", 4)]

        items = []
        async for row in triopg_conn.cursor("VALUES ($1, 1), ($2, 2), ($3, 3)",
                                            "1", "2", "3"):
            items.append(unwrap(row))
        assert items == [("1", 1), ("2", 2), ("3", 3)]


@pytest.mark.trio
async def test_transaction(triopg_conn, asyncpg_execute):
    # Execute without transaction
    await triopg_conn.execute(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE IF NOT EXISTS users (
            _id SERIAL PRIMARY KEY,
            user_id VARCHAR(32) UNIQUE
        )"""
    )
    assert await asyncpg_execute("SELECT * FROM users") == "SELECT 0"

    # Execute in transaction without exception
    async with triopg_conn.transaction():
        await triopg_conn.execute("INSERT INTO users (user_id) VALUES (1)")
    assert await asyncpg_execute("SELECT * FROM users") == "SELECT 1"

    # Execute in transaction raising exception, request should not be executed
    with pytest.raises(Exception):
        async with triopg_conn.transaction():
            await triopg_conn.execute("INSERT INTO users (user_id) VALUES (2)")
            raise Exception()

    assert await asyncpg_execute("SELECT * FROM users") == "SELECT 1"


@pytest.mark.trio
async def test_prepared_statement(triopg_conn):
    # Execute with prepared statement
    stmt = await triopg_conn.prepare("VALUES ($1, 2)")
    records = await stmt.fetchval("1")
    assert records == "1"

    # Test cursor in prepared statement
    async with triopg_conn.transaction():
        stmt = await triopg_conn.prepare(
            "VALUES ($1, 1), ($2, 2), ($3, 3), ($4, 4), ($5, 5)"
        )

        cursor = await stmt.cursor("1", "2", "3", "4", "5")
        row = await cursor.fetchrow()
        assert unwrap(row) == ("1", 1)
        advanced = await cursor.forward(1)
        assert advanced == 1
        fetched = await cursor.fetch(2)
        assert [unwrap(x) for x in fetched] == [("3", 3), ("4", 4)]

        items = []
        async for row in stmt.cursor("1", "2", "3", "4", "5"):
            items.append(unwrap(row))
        assert items == [("1", 1), ("2", 2), ("3", 3), ("4", 4), ("5", 5)]


@pytest.mark.trio
async def test_execute_many(triopg_conn, asyncpg_execute):
    await triopg_conn.execute(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE IF NOT EXISTS users (
            _id SERIAL PRIMARY KEY,
            user_id VARCHAR(32) UNIQUE
        )"""
    )

    user_ids = [(str(i),) for i in range(10)]
    await triopg_conn.executemany(
        "INSERT INTO users (user_id) VALUES ($1)", user_ids
    )

    assert await asyncpg_execute("SELECT * FROM users") == "SELECT 10"


@pytest.mark.trio
async def test_use_pool_without_acquire_connection(triopg_pool):
    rep = await triopg_pool.execute(
        """
        DROP TABLE IF EXISTS users;
        CREATE TABLE IF NOT EXISTS users (
            _id SERIAL PRIMARY KEY,
            user_id VARCHAR(32) UNIQUE
        )"""
    )
    assert rep == "CREATE TABLE"

    user_ids = [(str(i),) for i in range(10)]
    await triopg_pool.executemany(
        "INSERT INTO users (user_id) VALUES ($1)", user_ids
    )

    rep = await triopg_pool.fetch("SELECT * FROM users")
    rep = [dict(x.items()) for x in rep]
    assert rep == [{"_id": i + 1, "user_id": str(i)} for i in range(10)]

    rep = await triopg_pool.fetchrow("SELECT * FROM users WHERE _id = $1", 1)
    assert dict(rep.items()) == {"_id": 1, "user_id": "0"}

    val = await triopg_pool.fetchval(
        "SELECT user_id FROM users WHERE _id = $1", 2
    )
    assert val == "1"
