import logging

from fuocore.lyric import parse
from fuocore.utils import find_previous


logger = logging.getLogger(__name__)


class LiveLyric(object):
    def __init__(self, on_changed):
        self.on_changed = on_changed

        self._lyric = None
        self._pos_s_map = {}  # position sentence map
        self._pos_list = []  # position list
        self._pos = None

    # TODO: performance optimization?
    def on_position_changed(self, position):
        if not self._lyric:
            return

        pos = find_previous(position*1000 + 300, self._pos_list)
        if pos is not None and pos != self._pos:
            self.on_changed(self._pos_s_map[pos])
            self._pos = pos

    def on_song_changed(self, song):
        if song.lyric is None:
            self._lyric = None
            self._pos_s_map = {}
        else:
            self._lyric = song.lyric.content
            self._pos_s_map = parse(self._lyric)
        self._pos_list = sorted(list(self._pos_s_map.keys()))
        self._pos = None
