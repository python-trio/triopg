Release history
===============

.. currentmodule:: triopg

.. towncrier release notes start

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
