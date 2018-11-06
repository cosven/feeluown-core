# -*- coding: utf-8 -*-

"""
fuocore.player
--------------

This module difines :class:`.AbstractPlayer` ，and implement a :class:`.MpvPlayer`
based on mpv. In addition, it defines :class:`.Playlist` class, which is used
by the player to manage playlist.

**Simple Usage**

.. sourcecode:: python

    >>> from fuocore.player import MpvPlayer
    >>> player = MpvPlayer()
    >>> player.initialize()
    >>> player.play('xxx')  # local file path or http url
 """

from abc import ABCMeta, abstractmethod
from enum import IntEnum
import locale
import logging
import random

from mpv import MPV, MpvEventID, MpvEventEndFile, \
        _mpv_set_property_string

from fuocore.dispatch import Signal


logger = logging.getLogger(__name__)


class State(IntEnum):
    """
    Player states.
    """
    stopped = 0
    paused = 1
    playing = 2


class PlaybackMode(IntEnum):
    """
    Playlist playback mode.
    """
    one_loop = 0  #: One Loop
    sequential = 1  #: Sequential
    loop = 2  #: Loop
    random = 3  #: Random


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
        #: store value for ``current_song`` property
        self._current_song = None

        #: songs whose url is invalid
        self._bad_songs = []

        #: store value for ``songs`` property
        self._songs = songs or []

        #: store value for ``playback_mode`` property
        self._playback_mode = playback_mode

        #: playback mode changed signal
        self.playback_mode_changed = Signal()

        #: current song changed signal
        self.song_changed = Signal()

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        """overload [] operator"""
        return self._songs[index]

    def mark_as_bad(self, song):
        if song in self._songs and song not in self._bad_songs:
            self._bad_songs.append(song)

    def add(self, song):
        """往播放列表末尾添加一首歌曲"""
        if song in self._songs:
            return
        self._songs.append(song)
        logger.debug('Add %s to player playlist', song)

    def remove(self, song):
        """Remove song from playlist. O(n)

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

        if song in self._bad_songs:
            self._bad_songs.remove(song)

    def clear(self):
        """remove all songs from playlists"""

        self.current_song = None
        self._songs = []
        self._bad_songs.clear()

    def list(self):
        """get all songs in playlists"""
        return self._songs

    @property
    def current_song(self):
        """
        current playing song, return None if there is no current song
        """
        return self._current_song

    @current_song.setter
    def current_song(self, song):
        """设置当前歌曲，将歌曲加入到播放列表，并发出 song_changed 信号

        .. note::

            该方法理论上只应该被 Player 对象调用。
        """
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

    def _get_good_song(self, base=0, random_=False, direction=1):
        """从播放列表中获取一首可以播放的歌曲

        :param base: base index
        :param random: random strategy or not
        :param direction: forward if > 0 else backword

        >>> pl = Playlist([1, 2, 3])
        >>> pl._get_good_song()
        1
        >>> pl._get_good_song(base=1)
        2
        >>> pl._bad_songs = [2]
        >>> pl._get_good_song(base=1, direction=-1)
        1
        >>> pl._get_good_song(base=1)
        3
        >>> pl._bad_songs = [1, 2, 3]
        >>> pl._get_good_song()
        """
        if not self._songs or len(self._songs) <= len(self._bad_songs):
            logger.debug('No good song in playlist.')
            return None

        good_songs = []
        if direction > 0:
            song_list = self._songs[base:] + self._songs[0:base]
        else:
            song_list = self._songs[base::-1] + self._songs[:base:-1]
        for song in song_list:
            if song not in self._bad_songs:
                good_songs.append(song)
        if random_:
            return random.choice(good_songs)
        else:
            return good_songs[0]

    @property
    def next_song(self):
        """next song for player, calculated based on playback_mode"""
        # 如果没有正在播放的歌曲，找列表里面第一首能播放的
        if self.current_song is None:
            return self._get_good_song()

        if self.playback_mode == PlaybackMode.random:
            next_song = self._get_good_song(random_=True)
        else:
            current_index = self._songs.index(self.current_song)
            if current_index == len(self._songs) - 1:
                if self.playback_mode in (PlaybackMode.loop, PlaybackMode.one_loop):
                    next_song = self._get_good_song()
                elif self.playback_mode == PlaybackMode.sequential:
                    next_song = None
            else:
                next_song = self._get_good_song(base=current_index+1)
        return next_song

    @property
    def previous_song(self):
        """previous song for player to play

        NOTE: not the last played song
        """
        if self.current_song is None:
            return self._get_good_song(base=-1, direction=-1)

        if self.playback_mode == PlaybackMode.random:
            previous_song = self._get_good_song(direction=-1)
        else:
            current_index = self._songs.index(self.current_song)
            previous_song = self._get_good_song(base=current_index - 1, direction=-1)
        return previous_song


class AbstractPlayer(metaclass=ABCMeta):
    """Player abstrace base class"""

    def __init__(self, playlist=Playlist(), **kwargs):
        self._position = 0  # seconds
        self._volume = 100  # (0, 100)
        self._playlist = playlist
        self._state = State.stopped
        self._duration = None

        #: player position changed signal
        self.position_changed = Signal()

        #: player state changed signal
        self.state_changed = Signal()

        #: current song finished signal
        self.song_finished = Signal()

        #: duration changed signal
        self.duration_changed = Signal()

        #: media change signal
        self.media_changed = Signal()

    @property
    def state(self):
        """Player state

        :return: :class:`.State`
        """
        return self._state

    @state.setter
    def state(self, value):
        """set player state, emit state changed signal

        outer object should not set state directly,
        use ``pause`` / ``resume`` / ``stop`` / ``play`` method instead.
        """
        self._state = value
        self.state_changed.emit(value)

    @property
    def current_song(self):
        """当前正在播放的歌曲

        .. warning:

           即使
        """
        return self._playlist.current_song

    @property
    def playlist(self):
        """player playlist

        :return: :class:`.Playlist`
        """
        return self._playlist

    @property
    def position(self):
        """player position, the units is seconds"""
        return self._position

    @position.setter
    def position(self, position):
        """set player position, the units is seconds"""

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

    TODO: make me singleton
    """
    def __init__(self, audio_device=b'auto', *args, **kwargs):
        super(MpvPlayer, self).__init__()
        # https://github.com/cosven/FeelUOwn/issues/246
        locale.setlocale(locale.LC_NUMERIC, 'C')
        self._mpv = MPV(ytdl=False,
                        input_default_bindings=True,
                        input_vo_keyboard=True)

        _mpv_set_property_string(self._mpv.handle, b'audio-device', audio_device)

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
        self.song_finished.connect(self._on_song_finished)
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
        """播放指定歌曲

        如果目标歌曲与当前歌曲不相同，则修改播放列表当前歌曲，
        播放列表会发出 song_changed 信号，player 监听到信号后调用 play 方法，
        到那时才会真正的播放新的歌曲。如果和当前播放歌曲相同，则忽略。

        .. note::

            调用方不应该直接调用 playlist.current_song = song 来切换歌曲
        """
        if song is not None and song == self.current_song:
            logger.warning('The song is already under playing.')
        else:
            self._playlist.current_song = song

    def play_next(self):
        """播放下一首歌曲

        .. note::

            这里不能使用 ``play_song(playlist.next_song)`` 方法来切换歌曲，
            ``play_song`` 和 ``playlist.current_song = song`` 是有区别的。
        """
        self.playlist.current_song = self.playlist.next_song

    def play_previous(self):
        self.playlist.current_song = self.playlist.previous_song

    def replay(self):
        self.playlist.current_song = self.current_song

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
        logger.info('Player receive duration changed signal')
        self.duration = duration

    def _on_song_changed(self, song):
        """播放列表 current_song 发生变化后的回调

        判断变化后的歌曲是否有效的，有效则播放，否则将它标记为无效歌曲。
        如果变化后的歌曲是 None，则停止播放。
        """
        logger.debug('Player received song changed signal')
        if song is not None:
            logger.info('Try to play song: %s' % song)
            if song.url:
                self.play(song.url)
            else:
                self._playlist.mark_as_bad(song)
                self.play_next()
        else:
            self.stop()
            logger.info('No good song in player playlist anymore.')

    def _on_event(self, event):
        if event['event_id'] == MpvEventID.END_FILE:
            reason = event['event']['reason']
            logger.debug('Current song finished. reason: %d' % reason)
            if self.state != State.stopped and reason != MpvEventEndFile.ABORTED:
                self.song_finished.emit()

    def _on_song_finished(self):
        if self._playlist.playback_mode == PlaybackMode.one_loop:
            self.replay()
        else:
            self.play_next()
