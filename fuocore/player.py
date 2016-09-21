# -*- coding: utf-8 -*-

import logging
import subprocess


class Player(object):
    def __init__(self):
        super().__init__()

        self._handler = None
        self._position = 0

    @property
    def handler(self):
        if self._handler is None:
            try:
                self._handler = subprocess.Popen(['mpg123', '-R'],
                                                 stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
            except FileNotFoundError as e:
                raise RuntimeError('Cant find mpg123! Please install mpg123')
        return self._handler

    def destroy(self):
        if self._handler is not None:
            self._handler.stdin.write(b'q\n')
            self._handler.stdin.flush()
            self._handler.stdin.close()
            self._handler.wait()
        return True

    @property
    def position(self):
        pass

    def play(self):
        pass

    def toggle(self):
        pass

    def pause(self):
        pass

    def play_song(self, url):
        pass

    def next(self):
        pass

    def last(self):
        pass
