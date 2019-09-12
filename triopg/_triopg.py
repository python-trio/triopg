from functools import wraps, partial
import trio
import asyncpg
import trio_asyncio


def _shielded(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        with trio.open_cancel_scope(shield=True):
            return await f(*args, **kwargs)

    return wrapper


def connect(*args, **kwargs):
    return TrioConnectionProxy(*args, **kwargs)


def create_pool(*args, **kwargs):
    return TrioPoolProxy(*args, **kwargs)


class TrioTransactionProxy:
    def __init__(self, asyncpg_transaction):
        self._asyncpg_transaction = asyncpg_transaction

    @trio_asyncio.aio_as_trio
    async def __aenter__(self, *args):
        return await self._asyncpg_transaction.__aenter__(*args)

    @_shielded
    @trio_asyncio.aio_as_trio
    async def __aexit__(self, *args):
        return await self._asyncpg_transaction.__aexit__(*args)


class TrioConnectionProxy:
    def __init__(self, *args, **kwargs):
        self._asyncpg_create_connection = partial(
            asyncpg.connect, *args, **kwargs
        )
        self._asyncpg_conn = None

    def transaction(self, *args, **kwargs):
        asyncpg_transaction = self._asyncpg_conn.transaction(*args, **kwargs)
        return TrioTransactionProxy(asyncpg_transaction)

    def __getattr__(self, attr):
        target = getattr(self._asyncpg_conn, attr)

        if callable(target):

            @wraps(target)
            @trio_asyncio.aio_as_trio
            async def wrapper(*args, **kwargs):
                return await target(*args, **kwargs)

            # Only generate the function wrapper once per connection instance
            setattr(self, attr, wrapper)

            return wrapper

        return target

    @_shielded
    @trio_asyncio.aio_as_trio
    async def close(self):
        return await self._asyncpg_conn.close()

    async def __aenter__(self):
        if not self._asyncpg_conn:
            self._asyncpg_conn = await trio_asyncio.aio_as_trio(
                self._asyncpg_create_connection
            )()
        return self

    async def __aexit__(self, *exc):
        return await self.close()


class TrioPoolAcquireContextProxy:
    def __init__(self, asyncpg_acquire_context):
        self._asyncpg_acquire_context = asyncpg_acquire_context

    @trio_asyncio.aio_as_trio
    async def __aenter__(self, *args):
        proxy = await self._asyncpg_acquire_context.__aenter__(*args)
        conn_proxy = TrioConnectionProxy()
        conn_proxy._asyncpg_conn = proxy._con
        return conn_proxy

    @_shielded
    @trio_asyncio.aio_as_trio
    async def __aexit__(self, *args):
        return await self._asyncpg_acquire_context.__aexit__(*args)


class TrioPoolProxy:
    def __init__(self, *args, **kwargs):
        self._asyncpg_create_pool = partial(
            asyncpg.create_pool, *args, **kwargs
        )
        self._asyncpg_pool = None

    def acquire(self):
        return TrioPoolAcquireContextProxy(self._asyncpg_pool.acquire())

    async def execute(self, statement: str, *args, timeout: float = None):
        async with self.acquire() as conn:
            return await conn.execute(statement, *args, timeout=timeout)

    async def executemany(
            self, statement: str, args, *, timeout: float = None
    ):
        async with self.acquire() as conn:
            return await conn.executemany(statement, args, timeout=timeout)

    async def fetch(self, query, *args, timeout: float = None):
        async with self.acquire() as conn:
            return await conn.fetch(query, *args, timeout=timeout)

    async def fetchval(self, query, *args, timeout: float = None):
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args, timeout=timeout)

    async def fetchrow(self, query, *args, timeout: float = None):
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args, timeout=timeout)

    @_shielded
    @trio_asyncio.aio_as_trio
    async def close(self):
        return await self._asyncpg_pool.close()

    def terminate(self):
        return self._asyncpg_pool.terminate()

    async def __aenter__(self):
        if not self._asyncpg_pool:
            self._asyncpg_pool = await trio_asyncio.aio_as_trio(
                self._asyncpg_create_pool
            )()
        return self

    async def __aexit__(self, *exc):
        return await self.close()
