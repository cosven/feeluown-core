# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty
import os

from fuzzywuzzy import process
from mutagen.mp3 import EasyMP3

from .consts import MUSIC_LIBRARY_PATH
from .decorators import log_exectime
from .models import SongModel


providers = set()


class AbstractProvider(metaclass=ABCMeta):
    """abstract music resource provider"""

    @abstractproperty
    def name(self):
        """provider name, used to identify"""

    @abstractmethod
    def search(self, keyword, **kwargs):
        """search songs by name, artist name, album name

        :return: list of brief songs.
        """

    @abstractmethod
    def get_song(self, identifier):
        """get song by identifier

        :return: song model: :class:`fuocore.models.SongModel`
        """


class LocalProvider(AbstractProvider):

    def __init__(self, library_paths=[MUSIC_LIBRARY_PATH], depth=2):
        self._library_paths = library_paths
        self._library = list()
        self._songs = list()  # [(path, model)]
        self._identifier_song_map = dict()
        self.is_initialized = False

        # to initialize library
        self.library_paths = library_paths

    def _scan_dir(self, directory, exts=['mp3'], depth=1):
        if depth < 0:
            return []

        media_files = []
        for path in os.listdir(directory):
            path = os.path.join(directory, path)
            if os.path.isdir(path):
                files = self._scan_dir(path, exts, depth - 1)
                media_files.extend(files)
            elif os.path.isfile(path):
                if path.split('.')[-1] in exts:
                    media_files.append(path)
        return media_files

    @property
    def library_paths(self):
        return self._library_paths

    @library_paths.setter
    def library_paths(self, library_path):
        self._library = self.scan()
        self._songs = [self.model_from_fpath(fpath) for fpath in self._library]
        self._identifier_song_map.clear()
        if not self._identifier_song_map:
            for song in self._songs:
                self._identifier_song_map[song.identifier] = song

    @log_exectime
    def scan(self, exts=['mp3'], depth=1):
        """scan all media files in a directory"""
        depth = depth if depth <= 2 else 2
        media_files = []
        for directory in self._library_paths:
            media_files.extend(self._scan_dir(directory, exts, depth))
        return list(set(media_files))

    def add_to_library(self, directory):
        if directory not in self._library_paths:
            self._library_paths.append(directory)
        self.library_paths = self._library_paths

    @property
    def songs(self):
        return self._songs

    def model_from_fpath(self, fpath):
        metadata = EasyMP3(fpath)
        title = metadata['title'][0] if 'title' in metadata else 'unknown'
        artists_name = metadata['artist'] if 'artist' in metadata else ['unknown']
        brief_artists = [{'name': name} for name in artists_name]
        album_name = metadata['album'][0] if 'album' in metadata else 'unknown'
        brief_album = {'name': album_name}
        song = SongModel(name=title, brief_artists=brief_artists, url=fpath, brief_album=brief_album)
        song.source = self.name
        return song

    @property
    def name(self):
        return 'local'

    @log_exectime
    def search(self, keyword, limit=10):
        repr_song_map = dict()
        for song in self.songs:
            repr_song_map[str(song) + song.identifier] = song
        choices = repr_song_map.keys()
        result = process.extract(keyword, choices, limit=limit)
        result_songs = []
        for each, score in result:
            result_songs.append(repr_song_map[each])
        return result_songs

    def get_song(self, identifier):
        return self._identifier_song_map.get(identifier)


def register(provider):
    providers.add(provider)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)
