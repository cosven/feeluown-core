__version__ = '0.0.3a'


from .player import Player  # noqa
from .netease import Netease  # noqa
from .netease import netease  # noqa


__all__ = ['Player', 'netease', 'Netease']
