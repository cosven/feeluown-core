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

    async def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen()
        # make restart easier
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)

        event_loop = asyncio.get_event_loop()
        while True:
            conn, addr = await event_loop.sock_accept(sock)
            event_loop.create_task(self.handle_func(conn, addr))


if __name__ == '__main__':
    async def handle(conn, addr):
        event_loop = asyncio.get_event_loop()
        event_loop.sock_sendall(conn, b'OK feeluown 1.0.0a0')

        while True:
            command = await event_loop.sock_recv(conn, 1024)
            command = command.decode()
            if command.strip() in ('exit', 'quit'):
                conn.close()
                break


    server = TcpServer(handle_func=handle)
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(server.run())
    event_loop.run_forever()
