Release history
===============

.. currentmodule:: triopg

.. towncrier release notes start

Triopg 0.6.0 (2021-03-03)
-------------------------

Features
~~~~~~~~

- Add ``.listen`` helper for Trio-style handling of LISTEN notifications. (`#13 <https://github.com/python-trio/triopg/issues/13>`__)


Bugfixes
~~~~~~~~

- Correctly proxy ordinary (non-async) ``asyncpg.Connection`` methods.
  For example, ``.is_closed()``, ``.get_server_pid()`` etc. (`#11 <https://github.com/python-trio/triopg/issues/11>`__)
- Correctly proxy ordinary (non-async) ``PreparedStatement`` methods.
  For example, ``.get_statusmsg()``, ``.get_query()`` etc. (`#14 <https://github.com/python-trio/triopg/issues/14>`__)


Triopg 0.5.0 (2020-08-03)
-------------------------

Features
~~~~~~~~

- Add support for prepared statement and cursor (`#9 <https://github.com/python-trio/triopg/issues/9>`__)


Misc
~~~~

- `#5 <https://github.com/python-trio/triopg/issues/5>`__


Triopg 0.4.0 (2020-03-09)
-------------------------

-  Add ``Pool.fetchrow``, ``Pool.fetchval``, ``Pool.execute``,
   and ``Pool.executemany`` shortcuts.


Triopg 0.3.0 (2018-10-14)
-------------------------

-  Make ``connect`` and ``create_pool`` async context manager only to avoid
   crash due to asyncpg using __del__ to call on the asyncio loop
   (see https://github.com/python-trio/trio-asyncio/issues/44)


Triopg 0.2.1 (2018-10-03)
-------------------------

- Upgrade for compatibility with trio-asyncio>=0.9.0


Triopg 0.2.0 (2018-08-16)
-------------------------

Features
~~~~~~~~

- Republish asyncpg's exceptions.
- Introduce ``triopg.create_pool_cm`` to handle pool creation as an
  async context manager.

Bugfixes
~~~~~~~~

- Fix ``triopg.create_pool`` being used an async function.

Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- ``triopg.create_pool`` can no longer be used as an async context manager,
  ``triopg.create_pool_cm`` should be used instead.


Triopg 0.1.0 (2018-07-28)
-------------------------

No significant changes.
