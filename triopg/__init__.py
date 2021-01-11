"""Top-level package for triopg."""

from ._version import __version__
from ._triopg import connect, create_pool, NOTIFY_OVERFLOW
from .exceptions import *  # NOQA

__all__ = (
    '__version__',
    'connect',
    'create_pool',
    'NOTIFY_OVERFLOW',
) + exceptions.__all__  # NOQA
