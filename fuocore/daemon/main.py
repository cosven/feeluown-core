import asyncio
import logging

from fuocore.daemon.tcp_server import TcpServer
from fuocore.daemon.parser import CmdParser
from fuocore.daemon.handlers import exec_cmd
from fuocore.daemon.lyric_live_pub import LiveLyric


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
        logger.info('RECV: ' + command)
        cmd = CmdParser.parse(command)
        msg = exec_cmd(app, cmd)
        event_loop.sock_sendall(conn, bytes(msg, 'utf-8'))


async def handle_live_lyric(app, conn, addr):
    logger.info('live lyric')
    event_loop = asyncio.get_event_loop()
    event_loop.sock_sendall(conn, b'OK feeluown live lyric\n')
    player = app.player
    playlist = app.playlist

    q = asyncio.Queue(1)

    def send(s):
        q.put_nowait(s)

    livelyric = LiveLyric(send_func=send)
    player.position_changed.connect(app.livelyric.on_position_changed)
    playlist.song_changed.connect(app.livelyric.on_song_changed)
    while True:
        s = await q.get()
        try:
            event_loop.sock_sendall(s)
        except Exception as e:
            conn.close()
            import pdb; pdb.set_trace()
            break


async def run(app, *args, **kwargs):
    port = 23333
    host = '0.0.0.0'
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(
        TcpServer(host, port, handle_func=handle).run(app))


async def run_live_lyric_pubsub(app, *args, **kwargs):
    port = 22332
    host = '0.0.0.0'
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(
        TcpServer(host, port, handle_func=handle_live_lyric).run(app))
