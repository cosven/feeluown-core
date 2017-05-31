import logging
from logging import NullHandler

from .source import Source  # noqa


__all__ = ['Source']


logging.getLogger(__name__).addHandler(NullHandler())
