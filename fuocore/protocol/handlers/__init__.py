from abc import ABC, abstractmethod
import logging

from fuocore.core.player import PlaybackMode, State

from .helpers import show_songs, show_song


logger = logging.getLogger(__name__)


class CmdHandleException(Exception):
    pass


class CmdNotFound(CmdHandleException):
    pass


class InvalidFUri(CmdHandleException):
    pass


def exec_cmd(app, live_lyric, cmd):
    logger.debug('EXEC_CMD: ' + str(cmd))

    # 一些
    if cmd.action in ('help', ):
        handler = HelpHandler(app,
                              live_lyric=live_lyric)

    elif cmd.action in ('show', ):
        handler = ShowHandler(app,
                              live_lyric=live_lyric)

    elif cmd.action in ('search', ):
        handler = SearchHandler(app,
                                live_lyric=live_lyric)

    # 播放器相关操作
    elif cmd.action in (
        'play', 'pause', 'resume', 'stop', 'toggle',
    ):
        handler = PlayerHandler(app,
                                live_lyric=live_lyric)

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
        handler = PlaylistHandler(app,
                                  live_lyric=live_lyric)
    elif cmd.action in ('status',):
        handler = StatusHandler(app,
                                live_lyric=live_lyric)
    else:
        return 'Oops Command not found!\n'

    rv = 'ACK {}'.format(cmd.action)
    if cmd.args:
        rv += ' {}'.format(' '.join(cmd.args))
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
    def __init__(self, app, live_lyric):
        self.app = app
        self.live_lyric = live_lyric

    @abstractmethod
    def handle(self, cmd):
        pass


class SearchHandler(AbstractHandler):
    def handle(self, cmd):
        return self.search_songs(cmd.args[0])

    def search_songs(self, query):
        songs = self.app.source.search(query)
        return show_songs(songs)


class StatusHandler(AbstractHandler):
    def handle(self, cmd):
        player = self.app.player
        playlist = self.app.playlist
        live_lyric = self.live_lyric
        repeat = int(playlist.playback_mode in
                     (PlaybackMode.one_loop, PlaybackMode.loop))
        random = int(playlist.playback_mode == PlaybackMode.random)
        msgs = [
            'repeat:    {}'.format(repeat),
            'random:    {}'.format(random),
            'volume:    {}'.format(player.volume),
            'state:     {}'.format(player.state.name),
        ]
        if player.state in (State.paused, State.playing):
            msgs += [
                'duration:  {}'.format(player.duration),
                'position:  {}'.format(player.position),
                'song:      {}'.format(show_song(player.current_song, brief=True)),  # noqa
                'lyric-s:   {}'.format(live_lyric.current_sentence),
            ]
        return '\n'.join(msgs)


class PlayerHandler(AbstractHandler):
    def handle(self, cmd):
        if cmd.action == 'play':
            song_furi = cmd.args[0]
            return self.play_song(song_furi)
        elif cmd.action == 'pause':
            # FIXME: please follow ``Law of Demeter``
            self.app.player.pause()
        elif cmd.action == 'stop':
            self.app.player.stop()
        elif cmd.action == 'resume':
            self.app.player.resume()
        elif cmd.action == 'toggle':
            self.app.player.toggle()

    def play_song(self, song_furi):
        self.app.play(song_furi)


class PlaylistHandler(AbstractHandler):
    def handle(self, cmd):
        if cmd.action == 'add':
            return self.add(cmd.args[0])
        elif cmd.action == 'remove':
            return self.remove(cmd.args[0])
        elif cmd.action == 'clear':
            return self.clear()
        elif cmd.action == 'list':
            return self.list()
        elif cmd.action == 'next':
            self.app.playlist.play_next()
        elif cmd.action == 'previous':
            self.app.playlist.play_previous()

    def add(self, furis):
        playlist = self.app.playlist
        furi_list = furis.split(',')
        songs = self.app.source.list_songs(furi_list)
        for song in songs:
            playlist.add(song)

    def remove(self, song_id):
        song = self.app.source.get_song(song_id)
        self.app.playlist.remove(song)

    def list(self):
        songs = self.app.playlist.list()
        return show_songs(songs)

    def clear(self):
        self.app.playlist.clear()


class HelpHandler(AbstractHandler):
    def handle(self, cmd):
        return """
Available commands::

    search <string>  # search songs by <string>
    show fuo://xxx  # show xxx detail info
    play fuo://xxx/songs/yyy  # play yyy song
    list  # show player current playlist
    status  # show player status
    next  # play next song
    previous  # play previous song
    pause
    resume
    toggle

Watch live lyric::

    echo "sub topic.live_lyric" | nc host 23334
"""


from .show import ShowHandler  # noqa
