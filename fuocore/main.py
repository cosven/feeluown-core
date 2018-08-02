"""
main.py
~~~~~~~

基于 fuocore 提供的模块和功能，写的一个 DEMO 应用。
主要用于 fuocore 模块集成测试，非生产使用。
"""

import argparse
import asyncio
import logging
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


def setup_argparse():
    parser = argparse.ArgumentParser(description='运行 fuo 播放服务')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='开启调试模式')

    # XXX: 不知道能否加一个基于 regex 的 option？比如加一个
    # `--mpv-*` 的 option，否则每个 mpv 配置我都需要写一个 option？

    # TODO: 需要在文档中给出如何查看有哪些播放设备的方法
    parser.add_argument(
        '--mpv-audio-device',
        default='auto',
        help='（高级选项）给 mpv 播放器指定播放设备'
    )
    return parser


def main():
    parser = setup_argparse()
    args = parser.parse_args()

    debug = args.debug
    mpv_audio_device = args.mpv_audio_device

    setup_logger(debug=debug)

    player = MpvPlayer(audio_device=bytes(mpv_audio_device, 'utf-8'))
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
