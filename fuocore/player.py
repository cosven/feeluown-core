# -*- coding: utf-8 -*-

from enum import Enum
import logging
import threading
import subprocess

from .dispatch import Signal


class State(Enum):
    stopped = 0
    paused = 1
    playing = 2


class Player(object):
    '''mpg123 wrapper

    Each time the player play a song, it will kill the old process and open
    a new subprocess.
    '''
    def __init__(self):
        super().__init__()

        self._handler = None
        self._stdout_cap_thread = None

        self._position = 0
        self._state = State.stopped
        self._duration = 0

        self.finished = Signal()
        self.position_changed = Signal()
        self.state_changed = Signal()

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
                self._state = State.playing
                self.position_changed.emit()
            elif flag == '@P':
                a = line[3:4]
                if a == '0':
                    logging.info('Player stopped.')
                    self._state = State.stopped
                    self._duration = 0
                    self._position = 0
                    self.finished.emit()
                    self.destroy()
                    break
                elif a == '1':
                    logging.info('Player paused.')
                    self._state = State.paused
                else:
                    logging.info('Player resumed.')
                    self._state = State.playing
                self.state_changed.emit()
            elif flag == '@E':
                logging.warning('Player error occured.')

    def destroy(self):
        if self._handler is not None:
            self.handler.stdin.write(b'q\n')
            self.handler.stdin.flush()
            self.handler.stdin.close()
            self.handler.stdout.close()
            self.handler.stderr.close()
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

    def play_song(self, url):
        if self.state == State.playing:
            self.destroy()
        cmd = 'L {0}\n'.format(url)
        self.handler.stdin.write(cmd.encode('utf8'))
        self.handler.stdin.flush()
