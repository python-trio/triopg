"""Top-level package for triopg."""

from ._version import __version__
from ._triopg import connect, create_pool

__all__ = ('__version__', 'connect', 'create_pool')
