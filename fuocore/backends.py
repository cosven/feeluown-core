# -*- coding: utf-8 -*-
from functools import wraps
import logging

from .engine import AbstractPlayer, State, Playlist
from mpv import MPV

logger = logging.getLogger(__name__)


class MpvPlayer(AbstractPlayer):
    def __init__(self):
        super().__init__()
        self._mpv = MPV(ytdl=False,
                        input_default_bindings=True,
                        input_vo_keyboard=True)
        self._playlist = Playlist()

    def initialize(self):
        self._mpv.observe_property(
            'time-pos',
            lambda name, position: self._on_position_changed(position))
        self._mpv.register_event_callback(lambda event: self._on_song_finished(event))

    def quit(self):
        del self._mpv

    def play(self, url):
        self._mpv.play(url)
        self.state = State.playing

    def play_song(self, song):
        if self.playlist.current_song is not None and \
                self.playlist.current_song == song:
            logger.warning('the song to be played is same as current song')
            return
        self._playlist.add(song)
        self.play(song.url)

    def resume(self):
        self._mpv.pause = False
        self.state = State.playing

    def pause(self):
        self._mpv.pause = True
        self.state = State.paused

    def toggle(self):
        self._mpv.pause = not self._mpv.pause
        if self._mpv.pause:
            self.state = State.paused
        else:
            self.state = State.playing

    def stop(self):
        self._mpv.stop()
        self.state = State.stopped

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._mpv.seek(position)
        self._position = position

    def _on_position_changed(self, position):
        self._position = position
        self.position_changed.emit()

    def _on_song_finished(self, event):
        print(event)
        print('end_file')
