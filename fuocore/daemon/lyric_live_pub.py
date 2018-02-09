import asyncio
import logging

from fuocore.lyric import parse
from fuocore.utils import find_previous


logger = logging.getLogger(__name__)


class LiveLyric(object):
    def __init__(self, send_func):
        self.send = send_func

        self._lyric = None
        self._pos_s_map = {}  # position sentence map
        self._pos_list = []  # position list
        self._pos = None

    # TODO: performance optimization?
    def on_position_changed(self, position):
        logger.info('position -------------------')
        if not self._lyric:
            return

        if self._pos is None:
            pos = find_previous(position, self._pos_list)
            if pos is not None and pos != self._pos:
                self.send(self._pos_s_map[pos])

    def on_song_changed(self, song):
        logger.info('song !!!!!!!!!!!!!!!!!!!!!')
        if song.lyric is None:
            self._lyric = None
            self._pos_s_map = {}
        else:
            self._lyric = song.lyric.content
            self._pos_s_map = parse(self._lyric)
            logger.info('Lyric have been changed.')
        self._pos = None
