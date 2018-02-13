import logging
import socket
from threading import Thread

logger = logging.getLogger(__name__)


class TcpServer(object):
    def __init__(self, host, port, handle_func):
        self.host = host
        self.port = port
        self.handle_func = handle_func
        self.sock = None

    def run(self, *args, **kwargs):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock = sock
        while True:
            try:
                conn, addr = sock.accept()
            except ConnectionError as e:
                logger.warning(e)
                break
            logger.info('{} connected.'.format(addr))
            Thread(target=self.handle_func, args=(conn, addr, *args),
                   kwargs=kwargs).start()

    def close(self):
        if self.sock is not None:
            self.sock.close()
