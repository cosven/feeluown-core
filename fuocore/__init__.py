import logging

from .source import Source  # noqa


__version__ = '0.0.5a1'

__all__ = ['Source']


logging.basicConfig(level=logging.DEBUG)
