import asyncio
import logging
import sys

from fuocore import setup_logger
from fuocore.app import App
from fuocore.daemon import run, run_live_lyric_pubsub


def main():
    debug = '--debug' in sys.argv
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)
    logger.info('{} mode.'.format('Debug' if debug else 'Release'))
    app = App()
    app.initialize()
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app))
    event_loop.create_task(run_live_lyric_pubsub(app))
    event_loop.run_forever()


if __name__ == '__main__':
    main()
