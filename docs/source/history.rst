Release history
===============

.. currentmodule:: triopg

.. towncrier release notes start

Triopg 0.2.0 (2018-08-16)
-------------------------

Features
~~~~~~~~

- Republish asyncpg's exceptions.
- Introduce :func:`triopg.create_pool_cm` to handle pool creation as an
  async context manager.

Bugfixes
~~~~~~~~

- Fix :func:`triopg.create_pool` being used an async function.

Deprecations and Removals
~~~~~~~~~~~~~~~~~~~~~~~~~

- :func:`triopg.create_pool` can no longer be used as an async context manager,
  :func:`triopg.create_pool_cm` should be used instead.


Triopg 0.1.0 (2018-07-28)
-------------------------

No significant changes.
