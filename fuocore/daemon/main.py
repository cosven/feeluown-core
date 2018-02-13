import asyncio
import logging
import sys

from .aio_tcp_server import TcpServer
from .live_lyric import LiveLyric
from .pubsub import run as run_pubsub

from fuocore import setup_logger
from fuocore.app import App
from fuocore.protocol.parser import CmdParser
from fuocore.protocol.handlers import exec_cmd

logger = logging.getLogger(__name__)


async def handle(app, conn, addr):
    event_loop = asyncio.get_event_loop()
    event_loop.sock_sendall(conn, b'OK feeluown 1.0.0a0\n')
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
        msg = exec_cmd(app, cmd)
        event_loop.sock_sendall(conn, bytes(msg, 'utf-8'))


async def run(app, *args, **kwargs):
    port = 23333
    host = '0.0.0.0'
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(
        TcpServer(host, port, handle_func=handle).run(app))
    logger.info('Fuo daemon run in {}:{}'.format(host, port))


class LiveLyricPublisher(object):
    topic = 'topic.live_lyric'

    def __init__(self, gateway):
        self.gateway = gateway
        gateway.add_topic(self.topic)

    def publish(self, sentence):
        self.gateway.publish(sentence + '\n', self.topic)


def main():
    debug = '--debug' in sys.argv
    setup_logger(debug=debug)
    logger = logging.getLogger(__name__)
    logger.info('{} mode.'.format('Debug' if debug else 'Release'))

    app = App()
    app.initialize()

    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app))

    pubsub_gateway, pubsub_server = run_pubsub()  # runs in another thread
    live_lyric_publisher = LiveLyricPublisher(pubsub_gateway)

    live_lyric = LiveLyric(on_changed=live_lyric_publisher.publish)
    app.player.position_changed.connect(live_lyric.on_position_changed)
    app.playlist.song_changed.connect(live_lyric.on_song_changed)

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # NOTE: gracefully shutdown?
        pubsub_server.close()
        event_loop.close()


if __name__ == '__main__':
    main()
