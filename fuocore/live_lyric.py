import logging

from fuocore.dispatch import Signal
from fuocore.utils import find_previous

from .lyric import parse

logger = logging.getLogger(__name__)


class LiveLyric(object):
    """live lyric

    LiveLyric listens to song changed signal and position changed signal
    and emit sentence changed signal. It also has a ``current_sentence`` property.

    Usage::

        live_lyric = LiveLyric()
        player.song_changed.connect(live_lyric.on_song_changed)
        player.position_change.connect(live_lyric.on_position_changed)
    """
    def __init__(self):
        self.sentence_changed = Signal(str)

        self._lyric = None
        self._pos_s_map = {}  # position sentence map
        self._pos_list = []  # position list
        self._pos = None

        self._current_sentence = ''

    @property
    def current_sentence(self):
        """get current lyric sentence"""
        return self._current_sentence

    @current_sentence.setter
    def current_sentence(self, value):
        self._current_sentence = value
        self.sentence_changed.emit(value)

    # TODO: performance optimization?
    def on_position_changed(self, position):
        """bind position changed signal with this"""
        if not self._lyric:
            return

        pos = find_previous(position*1000 + 300, self._pos_list)
        if pos is not None and pos != self._pos:
            self.current_sentence = self._pos_s_map[pos]
            self._pos = pos

    def on_song_changed(self, song):
        """bind song changed signal with this"""
        if song is None or song.lyric is None:
            self._lyric = None
            self._pos_s_map = {}
        else:
            self._lyric = song.lyric.content
            self._pos_s_map = parse(self._lyric)
        self._pos_list = sorted(list(self._pos_s_map.keys()))
        self._pos = None
        self.current_sentence = ''
