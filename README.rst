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

PostgreSQL client for Trio based on asyncpg

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
