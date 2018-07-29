import asyncio
import logging
import sys
from fuocore import MpvPlayer
from fuocore.app import CliAppMixin, run_server
from fuocore.pubsub import run as run_pubsub
from fuocore.library import Library
from fuocore.local.provider import provider as lp
from fuocore.netease.provider import provider as np
from fuocore.qqmusic.provider import provider as qp


logger = logging.getLogger()


class BaseApp(object):
    def __init__(self, player, library, pubsub_gateway):
        self.player = player
        self.playlist = player.playlist
        self.library = library
        self.pubsub_gateway = pubsub_gateway


class App(CliAppMixin, BaseApp):
    def __init__(self, *args, **kwargs):
        BaseApp.__init__(self, *args, **kwargs)
        CliAppMixin.__init__(self)


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


def main():
    debug = '-d' in sys.argv
    setup_logger(debug=debug)

    player = MpvPlayer()
    player.initialize()
    library = Library()
    library.register(lp)
    library.register(np)
    library.register(qp)

    pubsub_gateway, pubsub_server = run_pubsub()

    app = App(player, library, pubsub_gateway)

    live_lyric = app.live_lyric
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run_server(app, live_lyric))
    try:
        event_loop.run_forever()
        logger.info('Event loop stopped.')
    except KeyboardInterrupt:
        # NOTE: gracefully shutdown?
        pass
    finally:
        pubsub_server.close()
        event_loop.close()
