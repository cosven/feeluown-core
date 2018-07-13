import asyncio
import logging
import sys
from collections import defaultdict
from urllib.parse import urlparse

from .aio_tcp_server import TcpServer
from .pubsub import run as run_pubsub

from fuocore import setup_logger
from fuocore import MpvPlayer
from fuocore import LiveLyric
from fuocore.core.furi import parse_furi
from fuocore.protocol.parser import CmdParser
from fuocore.protocol.handlers import exec_cmd
from fuocore.local.provider import provider as local_provider
from fuocore.netease.provider import provider as netease_provider

logger = logging.getLogger(__name__)


class Source(object):
    def __init__(self, prvs=[]):
        self.providers = set(prvs)

    def register(self, provider):
        self.providers.add(provider)

    def search(self, keyword):
        """search song by keyword"""
        songs = []
        for provider in self.providers:
            result = provider.search(keyword=keyword)
            _songs = list(result.songs[:20])
            logger.debug('在 provider({}) 中搜索到了 {} 首歌曲'
                         .format(provider.name, len(_songs)))
            songs.extend(_songs)
        logger.debug('共搜索到了 {} 首关于 {} 的歌曲'.format(len(songs), keyword))
        return songs

    def _get_provider(self, name):
        for provider in self.providers:
            if provider.identifier == name:
                return provider
        return None

    def get_song(self, furi_str):
        """get song from identifier"""
        result = urlparse(furi_str)
        provider = self._get_provider(result.netloc)
        identifier = result.path.split('/')[-1]
        return provider.Song.get(identifier)

    def list_songs(self, furi_str_list):
        provider_songs_map = defaultdict(list)
        for furi_str in furi_str_list:
            furi = parse_furi(furi_str)
            provider_songs_map[furi.provider].append(furi.identifier)
        songs = []
        for provider_name, identifiers in provider_songs_map.items():
            provider = self._get_provider(provider_name)
            songs += provider.Song.list(identifiers)
        return songs


class App(object):
    def __init__(self):
        self.player = MpvPlayer()
        self.playlist = self.player.playlist
        self.source = Source()

    def initialize(self):
        self.player.initialize()
        self.source.register(local_provider)
        self.source.register(netease_provider)

    def list_providers(self):
        for provider in self.source.providers:
            yield provider

    def get_provider(self, name):
        for provider in self.source.providers:
            if provider.identifier == name:
                return provider
        return None

    def play(self, song_identifier):
        song = self.source.get_song(song_identifier)
        if song is not None:
            self.player.play_song(song)


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

    pubsub_gateway, pubsub_server = run_pubsub()  # runs in another thread

    app = App()
    app.initialize()

    player = app.player

    live_lyric = LiveLyric()
    live_lyric_publisher = LiveLyricPublisher(pubsub_gateway)
    live_lyric.sentence_changed.connect(live_lyric_publisher.publish)
    player.position_changed.connect(live_lyric.on_position_changed)
    player.playlist.song_changed.connect(live_lyric.on_song_changed)

    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app, live_lyric))

    try:
        event_loop.run_forever()
    except KeyboardInterrupt:
        # NOTE: gracefully shutdown?
        pubsub_server.close()
        event_loop.close()


if __name__ == '__main__':
    main()
