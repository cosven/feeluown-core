# -*- coding: utf-8 -*-
import logging

from .engine import AbstractPlayer, State
from .mpv import MPV

logger = logging.getLogger(__name__)


class MpvPlayer(AbstractPlayer):
    def __init__(self):
        self._mpv = MPV(ytdl=False,
                        input_default_bindings=True,
                        input_vo_keyboard=True)

    def initialize(self):
        self._mpv.observe_property(
            'time-pos',
            lambda name, position: self._on_position_changed(position))

    def quit(self):
        del self._mpv

    def play(self, url):
        self._mpv.play(url)
        self._state = State.playing

    def play_song(self, song):
        if self._song == song:
            logger.warning('the song to be played is same as current song')
            return


    def resume(self):
        self._mpv.pause = False

    def pause(self):
        self._mpv.pause = True

    def toggle(self):
        self._mpv.pause = not self._mpv.pause

    def stop(self):
        pass

    def _on_position_changed(self, position):
        self._position = position
        self.position_changed.emit()
