.. image:: https://travis-ci.org/python-trio/triopg.svg?branch=master
   :target: https://travis-ci.org/python-trio/triopg
   :alt: Automated test status (Linux and MacOS)

.. image:: https://ci.appveyor.com/api/projects/status/4t8ydnax9p6ehauj/branch/master?svg=true
   :target: https://ci.appveyor.com/project/touilleMan/triopg/history
   :alt: Automated test status (Windows)

.. image:: https://codecov.io/gh/python-trio/triopg/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/python-trio/triopg
   :alt: Test coverage

triopg
======

Welcome to `triopg <https://github.com/python-trio/triopg>`__!

PostgreSQL client for `Trio <https://trio.readthedocs.io/>`__ based on
`asyncpg <https://magicstack.github.io/asyncpg/>`__.

License: Your choice of MIT or Apache License 2.0

Quick example:

.. code-block:: python

    import trio_asyncio
    import triopg


    async def main():
        async with triopg.connect() as conn:

            await conn.execute(
                """
                DROP TABLE IF EXISTS users;
                CREATE TABLE IF NOT EXISTS users (
                    _id SERIAL PRIMARY KEY,
                    user_id VARCHAR(32) UNIQUE
                )"""
            )

            async with conn.transaction():
                await conn.execute("INSERT INTO users (user_id) VALUES (1)")
                await conn.execute("INSERT INTO users (user_id) VALUES (2)")
                await conn.execute("INSERT INTO users (user_id) VALUES (3)")

            print(await conn.fetch("SELECT * FROM users"))


    trio_asyncio.run(main)

API basics
----------

``triopg`` is a thin Trio-compatible wrapper around ``asyncpg``. The API is the same,
with one exception - ``triopg`` does not support manual resource management.
In ``asyncpg`` you can manage pools, connections and transactions manually:

.. code-block:: python

    conn = await asyncpg.connect()
    tr = conn.transaction()
    # ..
    tr.commit()
    conn.close()

While in ``triopg`` you can *only* use ``async with`` blocks:

.. code-block:: python

    async with triopg.connect() as conn:
        async with conn.transaction():
            # ...

Otherwise you can follow ``asyncpg``
`tutorial <https://magicstack.github.io/asyncpg/current/usage.html>`__ and
`reference <https://magicstack.github.io/asyncpg/current/api/>`__.
Everything should work the same way. Please
`file an issue <https://github.com/python-trio/triopg/issues/new>`__ if it doesn't.

Helpers
-------

In addition to ``asyncpg``-compatible API, ``triopg`` provides Trio-style
``.listen()`` helper for the eponymous
`Postgres statement <https://www.postgresql.org/docs/current/sql-listen.html>`__:

.. code-block:: python

    async with conn.listen('some.channel', max_buffer_size=1) as notifications:
        async for notification in notifications:
            if notification != triopg.NOTIFY_OVERFLOW:
                print('Notification received:', notification)

``max_buffer_size`` is the amount of notifications you are willing to queue in memory.

If you **don't** want to think about buffering, set the buffer size to ``math.inf``
and everything will just work in regular non-pathological situations.

Otherwise, you can set a finite buffer. In this case you should handle
``triopg.NOTIFY_OVERFLOW`` marker and react according to your use case.
For example, you could re-scan the tables, like you would do at startup.
Or could you simply ignore the marker if you are only interested in the
newest notifications.

For detailed discussion on buffering, see Trio manual,
`"Buffering in channels" <https://trio.readthedocs.io/en/stable/reference-core.html#buffering-in-channels>`__
section.

**Note:** we can't politely ask Postgres to slow down: ``LISTEN`` backpressure is
`not supported by asyncpg <https://github.com/MagicStack/asyncpg/issues/463>`__.
There's also an inherent challenge with Postgres. Postgres (like most
broadcast systems) doesn't really have a good way to communicate backpressure
further upstream to the clients that are calling ``NOTIFY``.
