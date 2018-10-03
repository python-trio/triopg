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


@trio_asyncio.aio_as_trio
async def connect(*args, **kwargs):
    return TrioConnectionProxy(await asyncpg.connect(*args, **kwargs))


async def create_pool(*args, **kwargs):
    pool = TrioPoolProxy(*args, **kwargs)
    await pool._async__init__()
    return pool


def create_pool_cm(*args, **kwargs):
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
    def __init__(self, asyncpg_conn):
        self._asyncpg_conn = asyncpg_conn

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


class TrioPoolAcquireContextProxy:
    def __init__(self, asyncpg_acquire_context):
        self._asyncpg_acquire_context = asyncpg_acquire_context

    @trio_asyncio.aio_as_trio
    async def __aenter__(self, *args):
        proxy = await self._asyncpg_acquire_context.__aenter__(*args)
        return TrioConnectionProxy(proxy._con)

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

    @_shielded
    @trio_asyncio.aio_as_trio
    async def close(self):
        return await self._asyncpg_pool.close()

    def terminate(self):
        return self._asyncpg_pool.terminate()

    async def _async__init__(self):
        if not self._asyncpg_pool:
            self._asyncpg_pool = await trio_asyncio.aio_as_trio(
                self._asyncpg_create_pool
            )()
        return self._asyncpg_pool

    async def __aenter__(self):
        await self._async__init__()
        return self

    async def __aexit__(self, *exc):
        return await self.close()
