# -*- coding: utf-8 -*-

"""
    fuocore.player
    ~~~~~~~~~~~~~~

    fuocore media player.
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
import logging
import random

from mpv import MPV, MpvEventID, MpvEventEndFile

from fuocore.dispatch import Signal


logger = logging.getLogger(__name__)


class State(Enum):
    stopped = 0
    paused = 1
    playing = 2


class PlaybackMode(Enum):
    one_loop = 0
    sequential = 1
    loop = 2
    random = 3


class Playlist(object):
    """player playlist provide a list of song model to play

    NOTE - Design: Why we use song model instead of url? Theoretically,
    using song model may increase the coupling. However, simple url
    do not obtain enough metadata.
    """

    def __init__(self, songs=None, playback_mode=PlaybackMode.loop):
        """
        :param songs: list of :class:`fuocore.models.SongModel`
        :param playback_mode: :class:`fuocore.player.PlaybackMode`
        """
        self._current_song = None
        self._songs = songs or []
        self._playback_mode = playback_mode

        # signals
        self.playback_mode_changed = Signal()
        self.song_changed = Signal()

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        """overload [] operator"""
        return self._songs[index]

    def add(self, song):
        """insert a song after current song"""
        if song in self._songs:
            return

        if self._current_song is None:
            self._songs.append(song)
        else:
            index = self._songs.index(self._current_song)
            self._songs.insert(index + 1, song)
        logger.debug('Add %s to player playlist', song)

    def remove(self, song):
        """Remove song from playlist.

        If song is current song, remove the song and play next. Otherwise,
        just remove it.
        """
        if song in self._songs:
            if self._current_song is None:
                self._songs.remove(song)
            elif song == self._current_song:
                self.current_song = self.next_song
                self._songs.remove(song)
            else:
                self._songs.remove(song)
            logger.debug('Remove {} from player playlist'.format(song))
        else:
            logger.debug('Remove failed: {} not in playlist'.format(song))

    def clear(self):
        self.current_song = None
        self._songs = []

    def list(self):
        return self._songs

    @property
    def current_song(self):
        return self._current_song

    @current_song.setter
    def current_song(self, song):
        """change current song, emit song changed singal"""
        self._last_song = self.current_song
        if song is None:
            self._current_song = None
        # add it to playlist if song not in playlist
        elif song in self._songs:
            self._current_song = song
        else:
            self.add(song)
            self._current_song = song
        self.song_changed.emit(song)

    @property
    def playback_mode(self):
        return self._playback_mode

    @playback_mode.setter
    def playback_mode(self, playback_mode):
        self._playback_mode = playback_mode
        self.playback_mode_changed.emit(playback_mode)

    @property
    def next_song(self):
        next_song = None
        if not self._songs:
            return None
        if self.current_song is None:
            return self._songs[0]

        if self.playback_mode == PlaybackMode.random:
            next_song = random.choice(range(0, len(self._songs)))
        elif self.playback_mode == PlaybackMode.one_loop:
            next_song = self.current_song
        else:
            current_index = self._songs.index(self.current_song)
            if current_index == len(self._songs) - 1:
                if self.playback_mode == PlaybackMode.loop:
                    next_song = self._songs[0]
                elif self.playback_mode == PlaybackMode.sequential:
                    next_song = None
            else:
                next_song = self._songs[current_index + 1]
        return next_song

    @property
    def previous_song(self):
        """return to previous played song, if previous played song not exists,
        get the song before current song in playback mode order.
        """

        if not self._songs:
            return None
        if self.current_song is None:
            return self._songs[0]

        previous_song = None
        if self.playback_mode == PlaybackMode.random:
            previous_song = random.choice(self._songs)
        elif self.playback_mode == PlaybackMode.one_loop:
            previous_song = self.current_song
        else:
            current_index = self._songs.index(self.current_song)
            previous_song = self._songs[current_index - 1]
        return previous_song

    def play_next(self):
        self.current_song = self.next_song

    def play_previous(self):
        self.current_song = self.previous_song


class AbstractPlayer(metaclass=ABCMeta):

    def __init__(self, playlist=Playlist(), **kwargs):
        self._position = 0
        self._volume = 100  # (0, 100)
        self._playlist = playlist
        self._state = State.stopped
        self._duration = None

        self.position_changed = Signal()
        self.state_changed = Signal()
        self.song_finished = Signal()
        self.duration_changed = Signal()
        self.media_changed = Signal()

    @property
    def state(self):
        """player state

        :return: :class:`fuocore.engine.State`
        """
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        self.state_changed.emit(value)

    @property
    def current_song(self):
        return self._playlist.current_song

    @property
    def playlist(self):
        """player playlist

        :return: :class:`fuocore.engine.Playlist`
        """
        return self._playlist

    @playlist.setter
    def playlist(self, playlist):
        self._playlist = playlist

    @property
    def position(self):
        """player position, the units is seconds"""
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        value = 0 if value < 0 else value
        value = 100 if value > 100 else value
        self._volume = value

    @property
    def duration(self):
        """player media duration, the units is seconds"""
        return self._duration

    @duration.setter
    def duration(self, value):
        if value is not None and value != self._duration:
            self._duration = value
            self.duration_changed.emit(value)

    @abstractmethod
    def play(self, url):
        """play media

        :param url: a local file absolute path, or a http url that refers to a
            media file
        """

    @abstractmethod
    def play_song(self, song):
        """play media by song model

        :param song: :class:`fuocore.models.SongModel`
        """

    @abstractmethod
    def resume(self):
        """play playback"""

    @abstractmethod
    def pause(self):
        """pause player"""

    @abstractmethod
    def toggle(self):
        """toggle player state"""

    @abstractmethod
    def stop(self):
        """stop player"""

    @abstractmethod
    def initialize(self):
        """"initialize player"""

    @abstractmethod
    def shutdown(self):
        """shutdown player, do some clean up here"""


class MpvPlayer(AbstractPlayer):
    """

    player will always play playlist current song. player will listening to
    playlist ``song_changed`` signal and change the current playback.
    """
    def __init__(self):
        super(MpvPlayer, self).__init__()
        self._mpv = MPV(ytdl=False,
                        input_default_bindings=True,
                        input_vo_keyboard=True)
        self._playlist = Playlist()
        self._playlist.song_changed.connect(self._on_song_changed)

    def initialize(self):
        self._mpv.observe_property(
            'time-pos',
            lambda name, position: self._on_position_changed(position)
        )
        self._mpv.observe_property(
            'duration',
            lambda name, duration: self._on_duration_changed(duration)
        )
        # self._mpv.register_event_callback(lambda event: self._on_event(event))
        self._mpv.event_callbacks.append(self._on_event)
        self.song_finished.connect(self._playlist.play_next)
        logger.info('Player initialize finished.')

    def shutdown(self):
        del self._mpv

    def play(self, url):
        # NOTE - API DESGIN: we should return None, see
        # QMediaPlayer API reference for more details.

        logger.debug("Player will play: '%s'", url)

        # Clear playlist before play next song,
        # otherwise, mpv will seek to the last position and play.
        self._mpv.playlist_clear()
        self._mpv.play(url)
        self._mpv.pause = False
        self.state = State.playing
        self.media_changed.emit(url)

    def play_song(self, song):
        if self.playlist.current_song is not None and \
                self.playlist.current_song == song:
            logger.warning('the song to be played is same as current song')
            return

        url = song.url
        if url is not None:
            self._playlist.current_song = song
        else:
            raise ValueError("invalid song: song url can't be None")

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
        logger.info('stop player...')
        self._mpv.pause = True
        self.state = State.stopped
        self._mpv.playlist_clear()

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._mpv.seek(position, reference='absolute')
        self._position = position

    @AbstractPlayer.volume.setter
    def volume(self, value):
        super(MpvPlayer, MpvPlayer).volume.__set__(self, value)
        self._mpv.volume = self.volume

    def _on_position_changed(self, position):
        self._position = position
        self.position_changed.emit(position)

    def _on_duration_changed(self, duration):
        """listening to mpv duration change event"""
        logger.info('player receive duration changed signal')
        self.duration = duration

    def _on_song_changed(self, song):
        logger.debug('player received song changed signal')
        if song is not None:
            logger.info('Will play song: %s' % self._playlist.current_song)
            self.play(song.url)
        else:
            self.stop()
            logger.info('playlist provide no song anymore.')

    def _on_event(self, event):
        if event['event_id'] == MpvEventID.END_FILE:
            reason = event['event']['reason']
            logger.debug('Current song finished. reason: %d' % reason)
            if self.state != State.stopped and reason != MpvEventEndFile.ABORTED:
                self.song_finished.emit()
