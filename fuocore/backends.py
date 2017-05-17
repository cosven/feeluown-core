# -*- coding: utf-8 -*-

from .engine import AbstractPlayer, State
from .mpv import MPV


class MpvPlayer(AbstractPlayer):
    def __init__(self):
        self._mpv = MPV(ytdl=False,
                        input_default_bindings=True,
                        input_vo_keyboard=True)

    def initialize(self):
        self._mpv.observe_property(
            'time-pos',
            self._on_position_changed)

    def play(self, url):
        self._mpv.play(url)
        self._state = State.playing

    def play_song(self, song):
        pass

    def resume(self):
        self._mpv.pause = False

    def pause(self):
        self._mpv.pause = True

    def toggle(self):
        self._mpv.pause = not self._mpv.pause

    def stop(self):
        pass

    def quit(self):
        del self._mpv

    def _on_position_changed(self, position):
        print(position)
