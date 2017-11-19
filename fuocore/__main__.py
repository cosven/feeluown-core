import asyncio
import logging
import sys

from fuocore import setup_logger
from fuocore.app import App
from fuocore.provider import register
from fuocore.daemon import run
from fuocore.local.provider import LocalProvider
from fuocore.netease.provider import NeteaseProvider


def main():
    debug = '--debug' in sys.argv
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)
    logger.info('{} mode.'.format('Debug' if debug else 'Release'))
    app = App()
    app.player.initialize()
    local_provider = LocalProvider()
    netease_provider = NeteaseProvider()
    register(local_provider)
    register(netease_provider)
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app))
    event_loop.run_forever()


if __name__ == '__main__':
    main()
