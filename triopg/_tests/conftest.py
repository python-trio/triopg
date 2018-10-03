import pytest
import trio_asyncio
import asyncpg
from asyncpg.cluster import Cluster
import tempfile

import triopg


@pytest.fixture()
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
    conn = await trio_asyncio.aio_as_trio(asyncpg.connect
                                          )(**postgresql_connection_specs)
    try:
        yield conn
    finally:
        await trio_asyncio.aio_as_trio(conn.close)()


@pytest.fixture()
async def triopg_conn(asyncio_loop, postgresql_connection_specs):
    conn = await triopg.connect(**postgresql_connection_specs)
    try:
        yield conn
    finally:
        await conn.close()
