from abc import ABC, abstractmethod
import logging

from fuocore.daemon.handlers.helpers import show_songs


logger = logging.getLogger(__name__)


class CmdHandleException(Exception):
    pass


class CmdNotFound(CmdHandleException):
    pass


class InvalidFUri(CmdHandleException):
    pass


def exec_cmd(app, cmd):
    logger.info('EXEC_CMD: ' + str(cmd))

    # 一些
    if cmd.action in ('show', ):
        handler = ShowHandler(app)

    elif cmd.action in ('search', ):
        handler = SearchHandler(app)

    # 播放器相关操作
    elif cmd.action in (
        'play', 'pause', 'resume', 'stop',
    ):
        handler = PlayerHandler(app)

    # 播放列表相关命令
    elif cmd.action in (
        'add', 'remove', 'clear', 'list',
        'next', 'previous',
    ):
        """
        add/remove fuo://local:song:xxx
        create xxx

        set playback_mode=random
        set volume=100
        """
        handler = PlaylistHandler(app)
    else:
        return 'Oops\nCommand not found!'

    rv = 'ACK {} {}'.format(cmd.action, ' '.join(cmd.args))
    try:
        cmd_rv = handler.handle(cmd)
        if cmd_rv:
            rv += '\n' + cmd_rv
    except Exception as e:
        logger.exception('handle cmd({}) error'.format(cmd))
        return '\nOops\n'
    else:
        rv = rv or ''
        return rv + '\nOK\n'


class AbstractHandler(ABC):
    def __init__(self, app):
        self.app = app

    @abstractmethod
    def handle(self, cmd):
        pass


class SearchHandler(AbstractHandler):
    def handle(self, cmd):
        return self.search_songs(cmd.args[0])

    def search_songs(self, query):
        songs = self.app.source.search(query)
        return show_songs(songs)

class PlayerHandler(AbstractHandler):
    def handle(self, cmd):
        if cmd.action == 'play':
            song_furi = cmd.args[0]
            return self.play_song(song_furi)
        elif cmd.action == 'pause':
            self.app.player.pause()
        elif cmd.action == 'stop':
            self.app.player.stop()
        elif cmd.action == 'resume':
            self.app.player.resume()

    def play_song(self, song_furi):
        self.app.play(song_furi)


class PlaylistHandler(AbstractHandler):
    def handle(self, cmd):
        if cmd.action == 'add':
            return self.add(cmd.args[0])
        elif cmd.action == 'clear':
            return self.clear()
        elif cmd.action == 'list':
            return self.list()
        elif cmd.action == 'next':
            self.app.playlist.next()

    def add(self, song_furi):
        song = self.app.source.get_song(song_furi)
        self.app.playlist.add(song)

    def list(self):
        songs = self.app.playlist.list()
        return show_songs(songs)

    def clear(self):
        self.app.playlist.clear()


from fuocore.daemon.handlers.show import ShowHandler
