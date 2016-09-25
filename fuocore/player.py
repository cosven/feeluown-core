# -*- coding: utf-8 -*-

from enum import Enum
import logging
import random
import subprocess
import threading

from .dispatch import Signal
from .base_model import SongModel


class State(Enum):
    stopped = 0
    paused = 1
    playing = 2


class PlaybackMode(Enum):
    one_loop = 0
    sequential = 1
    loop = 2
    random = 3


class _SimpleSongModel(SongModel):
    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url


class Player(object):
    '''mpg123 wrapper

    Each time the player play a song, it will kill the old process and open
    a new subprocess.

    TODO: maybe we need a `Playlist` class
    '''
    def __init__(self):
        super().__init__()

        self._handler = None
        self._stdout_cap_thread = None

        self._position = 0
        self._state = State.stopped
        self._last_state = self._state
        self._duration = 0
        self._playback_mode = PlaybackMode.loop
        self._last_playback_mode = self._playback_mode

        # no repetition but ordering
        self._songs = []
        # current_song is None or `SongModel` instance and must in `_songs` list
        self._current_song = None

        self.finished = Signal()
        self.position_changed = Signal()
        self.state_changed = Signal()

        self.finished.connect(self.__play_next)

    @property
    def handler(self):
        if self._handler is None:
            try:
                self._handler = subprocess.Popen(['mpg123', '-R'],
                                                 stdin=subprocess.PIPE,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                self._stdout_cap_thread = threading.Thread(
                        target=self._capture_stdout, args=())
                self._stdout_cap_thread.start()
            except FileNotFoundError as e:
                raise RuntimeError('Cant find mpg123! Please install mpg123')
        return self._handler

    def _capture_stdout(self):
        while True:
            try:
                line = self._handler.stdout.readline().decode('utf8')
            except ValueError as e:
                break
            flag = line[:2]
            if flag == '@F':
                framecount, frame_left, sec, sec_left = line[3:].split(' ')
                self._position = float(sec)
                if int(framecount) == 0:
                    self._duration = float(sec_left)
                self.set_state(State.playing)
                self.position_changed.emit()
            elif flag == '@P':
                a = line[3:4]
                if a == '0':
                    logging.info('Player stopped.')
                    self.set_state(State.stopped)
                    self._duration = 0
                    self._position = 0
                    self.finished.emit()
                    break
                elif a == '1':
                    logging.info('Player paused.')
                    self.set_state(State.paused)
                else:
                    logging.info('Player resumed.')
                    self.set_state(State.playing)
            elif flag == '@E':
                logging.warning('Player error occured.')

    def destroy(self):
        if self._handler is not None:
            try:
                self.handler.stdin.write(b'q\n')
                self.handler.stdin.flush()
                self.handler.stdin.close()
                self.handler.stdout.close()
                self.handler.stderr.close()
            except ValueError:
                pass
            self._stdout_cap_thread.join()
            self._stdout_cap_thread = None
            self.handler.wait()
            self.handler.kill()
            self._handler = None
        return True

    @property
    def position(self):
        return self._position

    @property
    def duration(self):
        return self._duration

    @property
    def state(self):
        return self._state

    @property
    def playback_mode(self):
        return self._playback_mode

    @property
    def current_song(self):
        return self._current_song

    @property
    def songs(self):
        return self._songs

    def play(self):
        if self.state == State.paused:
            self.toggle()
            return True
        return False

    def toggle(self):
        self.handler.stdin.write(b'p\n')
        self.handler.stdin.flush()

    def pause(self):
        if self.state == State.playing:
            self.toggle()
            return True
        return False

    def stop(self):
        self.destroy()

    def set_state(self, state):
        self._state = state
        if self._last_state != state:
            self.state_changed.emit()
            self._last_state = state

    def _play(self, url):
        self.destroy()
        cmd = 'L {0}\n'.format(url)
        self.handler.stdin.write(cmd.encode('utf8'))
        self.handler.stdin.flush()

    def play_song(self, song):
        self._play(song.url)
        self._current_song = song
        self.add_song(song)

    def play_songs(self, songs):
        self._songs = songs
        if self._songs:
            self.play_song(self._songs[0])

    def _get_song(self, song):
        '''get song instance in `_songs` list'''
        for i, m in enumerate(self._songs):
            if song.mid == m.mid:
                return song
        return None

    def add_song(self, song, insert=False):
        if self._get_song(song) is None:
            if insert:
                if self._current_song is None:
                    index = 0
                else:
                    current_index = self._songs.index(self._current_song)
                    index = current_index + 1
                self._songs.insert(index, song)
            else:
                self._songs.append(song)
            return True
        return False

    def remove_song(self, song):
        song = self._get_song(song)
        if song is None:
            return None
        self._songs.remove(song)
        return True

    def get_previous_song(self):
        if not self._songs:
            return None
        if self.playback_mode == PlaybackMode.one_loop:
            return self._current_song
        elif self.playback_mode == PlaybackMode.loop:
            current_index = self._songs.index(self._current_song)
            if current_index == 0:
                return self._songs[-1]
            else:
                return current_index - 1
        elif self.playback_mode == PlaybackMode.sequential:
            return None
        else:
            return random.choice(self._songs)

    def get_next_song(self):
        if not self._songs:
            return None
        if self.playback_mode == PlaybackMode.one_loop:
            return self._current_song
        elif self.playback_mode == PlaybackMode.loop:
            if self._current_song == self._songs[-1]:
                return self._songs[0]
            else:
                return self._songs[self._songs.index(self._current_song) + 1]
        elif self.playback_mode == PlaybackMode.sequential:
            self.signal_playlist_finished.emit()
            return None
        else:
            return random.choice(self._songs)

    def __play_next(self):
        '''on song finished callback'''
        song = self.get_next_song()
        if song is not None:
            self.play_song(song)
