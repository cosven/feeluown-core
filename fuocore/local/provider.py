# -*- coding: utf-8 -*-

import logging
import os

from fuzzywuzzy import process
from marshmallow.exceptions import ValidationError
from mutagen import MutagenError
from mutagen.mp3 import EasyMP3

from fuocore.provider import AbstractProvider
from fuocore.consts import MUSIC_LIBRARY_PATH
from fuocore.utils import log_exectime

from fuocore.local.schemas import EasyMP3MetadataSongSchema
from fuocore.models import (
    BaseModel, SearchModel, SongModel, AlbumModel, ArtistModel
)


logger = logging.getLogger(__name__)


def scan_directory(directory, exts=None, depth=2):
    exts = exts or ['mp3']
    if depth < 0:
        return []

    media_files = []
    if not os.path.exists(directory):
        return []
    for path in os.listdir(directory):
        path = os.path.join(directory, path)
        if os.path.isdir(path):
            files = scan_directory(path, exts, depth - 1)
            media_files.extend(files)
        elif os.path.isfile(path):
            if path.split('.')[-1] in exts:
                media_files.append(path)
    return media_files


def create_song(fpath):
    """
    parse music file metadata with Easymp3 and return a song
    model.
    """
    try:
        metadata = EasyMP3(fpath)
    except MutagenError as e:
        logger.error('Mutagen parse metadata failed, ignore.')
        logger.debug(str(e))
        return

    schema = EasyMP3MetadataSongSchema(strict=True)
    metadata_dict = dict(metadata)
    if 'title' not in metadata_dict:
        title = [fpath.rsplit('/')[-1].split('.')[0], ]
        metadata_dict['title'] = title
    metadata_dict.update(dict(
        url=fpath,
        duration=metadata.info.length * 1000  # milesecond
    ))
    try:
        song, _ = schema.load(metadata_dict)
    except ValidationError:
        logger.exeception('解析音乐文件({}) 元数据失败'.format(fpath))
    return song


class LocalProvider(AbstractProvider):

    def __init__(self, library_paths=None, depth=2):
        self._library_paths = library_paths

        self._songs = list()

        self._identifier_song_map = dict()
        self._identifier_album_map = dict()
        self._identifier_artist_map = dict()

        self.library_paths = library_paths or [MUSIC_LIBRARY_PATH]

    @property
    def library_paths(self):
        return self._library_paths

    @library_paths.setter
    def library_paths(self, library_paths):
        self._library_paths = library_paths
        self._songs = self.scan()
        self.setup_library()

    def setup_library(self):
        self._identifier_song_map.clear()
        self._identifier_album_map.clear()
        self._identifier_artist_map.clear()

        if not self._identifier_song_map:
            for song in self._songs:
                self._identifier_song_map[song.identifier] = song
                if song.album is not None:
                    album = song.album
                    self._identifier_album_map[album.identifier] = album
                if song.artists is not None:
                    for artist in song.artists:
                        self._identifier_artist_map[artist.identifier] = artist

    @log_exectime
    def scan(self, exts=['mp3'], depth=2):
        """scan media files in all library_paths
        """
        depth = depth if depth <= 3 else 3
        media_files = []
        for directory in self._library_paths:
            logger.debug('正在扫描目录({})...'.format(directory))
            media_files.extend(scan_directory(directory, exts, depth))
        songs = []
        for fpath in media_files:
            song = create_song(fpath)
            if song is not None:
                songs.append(song)
            else:
                logger.warning('{} can not be recognized'.format(fpath))
        logger.debug('扫描到 {} 首歌曲'.format(len(songs)))
        return songs

    @property
    def songs(self):
        return self._songs

    @property
    def identifier(self):
        return 'local'

    @property
    def name(self):
        return '本地音乐'

    @log_exectime
    def search(self, keyword, **kwargs):
        limit = kwargs.get('limit', 10)
        repr_song_map = dict()
        for song in self.songs:
            key = song.title + ' ' + song.artists_name + str(song.identifier)
            repr_song_map[key] = song
        choices = repr_song_map.keys()
        result = process.extract(keyword, choices, limit=limit)
        result_songs = []
        for each, score in result:
            # if score > 80, keyword is almost included in song key
            if score > 80:
                result_songs.append(repr_song_map[each])
        return SearchModel(q=keyword, source='local', songs=result_songs)


provider = LocalProvider()


class NBaseModel(BaseModel):
    class Meta:
        provider = provider


class LSongModel(SongModel, BaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_song_map.get(identifier)

    @classmethod
    def list(cls, identifiers):
        return map(cls._meta.provider._identifier_song_map.get, identifiers)


class LAlbumModel(AlbumModel, BaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_album_map.get(identifier)


class LArtistModel(ArtistModel, BaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_artist_map.get(identifier)
