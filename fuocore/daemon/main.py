import asyncio
import logging

from fuocore.daemon.tcp_server import TcpServer
from fuocore.daemon.parser import CmdParser
from fuocore.daemon.handlers import exec_cmd


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
        if command in ('exit', 'quit'):
            conn.close()
            break
        logger.info('RECV: ' + command)
        cmd = CmdParser.parse(command)
        msg = exec_cmd(app, cmd)
        event_loop.sock_sendall(conn, bytes(msg, 'utf-8'))


async def run(app, *args, **kwargs):
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(TcpServer(handle_func=handle).run(app))


def main():
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run())
    event_loop.run_forever()


if __name__ == '__main__':
    main()
