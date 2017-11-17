import asyncio
import logging
import socket


logger = logging.getLogger(__name__)

PORT = 23333
HOST = '0.0.0.0'


class TcpServer(object):
    """
    目前是用相对非常底层的接口来实现功能，熟悉了之后可以考虑封装好的
    API。
    """
    def __init__(self, handle_func):
        self.handle_func = handle_func

    async def run(self, app):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen()
        # make restart easier
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)

        event_loop = asyncio.get_event_loop()
        while True:
            conn, addr = await event_loop.sock_accept(sock)
            event_loop.create_task(self.handle_func(app, conn, addr))
