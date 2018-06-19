import logging
import logging.config
# from logging import NullHandler

from fuocore.models import ModelType  # noqa
from fuocore.core.source import Source  # noqa
from fuocore.core.player import (
    MpvPlayer,
    State as PlayerState,
    PlaybackMode,
    Playlist,
)  # noqa
from fuocore.core.live_lyric import LiveLyric  # noqa


__all__ = [
    'Source',
    'MpvPlayer',
    'PlayerState',
    'PlaybackMode',
    'Playlist',
    'LiveLyric',
    'ModelType',
]


dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(levelname)s] "
                      "[%(module)s %(funcName)s %(lineno)d] "
                      ": %(message)s",
        },
    },
    'handlers': {
        'debug': {
            'formatter': 'standard',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'release': {
            'formatter': 'standard',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'fuocore': {
            'handlers': ['debug'],
            'level': logging.DEBUG,
            'propagate': True
        }
    }
}


def setup_logger(debug=True):
    if debug:
        logging.config.dictConfig(dict_config)
    else:
        dict_config['loggers']['fuocore']['handlers'] = ['release']
        logging.config.dictConfig(dict_config)


# logging.getLogger(__name__).addHandler(NullHandler())
