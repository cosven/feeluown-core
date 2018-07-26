import asyncio
import logging
import sys
from fuocore import MpvPlayer
from fuocore.library import Library
from fuocore.local.provider import provider as lp
from fuocore.netease.provider import provider as np
from fuocore.qqmusic.provider import provider as qp

from .app import CliMixin, run, run_pubsub


logger = logging.getLogger()


class App(CliMixin):
    def __init__(self, player, library, pubsub_gateway):
        self.player = player
        self.playlist = player.playlist
        self.library = library

        CliMixin.__init__(self, pubsub_gateway)


def main():
    from fuocore import setup_logger

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

    live_lyric = app._live_lyric
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app, live_lyric))
    try:
        event_loop.run_forever()
        logger.info('Event loop stopped.')
    except KeyboardInterrupt:
        # NOTE: gracefully shutdown?
        pass
    finally:
        pubsub_server.close()
        event_loop.close()
