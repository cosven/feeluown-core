"""
fuocore.app
~~~~~~~~~~~
"""

import asyncio
import logging
import sys
from collections import defaultdict
from urllib.parse import urlparse

from fuocore.aio_tcp_server import TcpServer
from fuocore.pubsub import run as run_pubsub

from fuocore import setup_logger
from fuocore import MpvPlayer
from fuocore import LiveLyric
from fuocore.furi import parse_furi
from fuocore.protocol.parser import CmdParser
from fuocore.protocol.handlers import exec_cmd

logger = logging.getLogger(__name__)


class LiveLyricPublisher(object):
    topic = 'topic.live_lyric'

    def __init__(self, gateway):
        self.gateway = gateway
        gateway.add_topic(self.topic)

    def publish(self, sentence):
        self.gateway.publish(sentence + '\n', self.topic)


class CliMixin(object):
    def __init__(self, pubsub_gateway):
        live_lyric = LiveLyric()
        live_lyric_publisher = LiveLyricPublisher(pubsub_gateway)
        live_lyric.sentence_changed.connect(live_lyric_publisher.publish)
        self.player.position_changed.connect(live_lyric.on_position_changed)
        self.playlist.song_changed.connect(live_lyric.on_song_changed)
        self._live_lyric = live_lyric
        self._live_lyric_publisher = live_lyric_publisher

    def list_providers(self):
        return self.library.list()

    def get_provider(self, name):
        # XXX: maybe this interface should removed
        return self.library.get(name)


async def handle(conn, addr, app, live_lyric):
    event_loop = asyncio.get_event_loop()
    event_loop.sock_sendall(conn, b'OK feeluown 1.0.0\n')
    while True:
        try:
            command = await event_loop.sock_recv(conn, 1024)
        except ConnectionResetError:
            logger.debug('客户端断开连接')
            break
        command = command.decode().strip()
        # NOTE: we will never recv empty byte unless
        # client close the connection
        if not command:
            conn.close()
            break
        logger.debug('RECV: ' + command)
        cmd = CmdParser.parse(command)
        msg = exec_cmd(app, live_lyric, cmd)
        event_loop.sock_sendall(conn, bytes(msg, 'utf-8'))


async def run(app, live_lyric, *args, **kwargs):
    port = 23333
    host = '0.0.0.0'
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(
        TcpServer(host, port, handle_func=handle).run(app, live_lyric))
    logger.info('Fuo daemon running at {}:{}'.format(host, port))
