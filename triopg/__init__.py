"""Top-level package for triopg."""

from ._version import __version__
from ._triopg import connect, create_pool
from .exceptions import *  # NOQA

__all__ = (
    '__version__',
    'connect',
    'create_pool',
) + exceptions.__all__  # NOQA
