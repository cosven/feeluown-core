# -*- coding: utf-8 -*-

"""
TODO: 这个模块中目前逻辑非常多，包括音乐目录扫描、音乐库的构建等小部分，
这些小部分理论都可以从中拆除。
"""

import logging
import pickle
import os

from fuzzywuzzy import process
from marshmallow.exceptions import ValidationError
from mutagen import MutagenError
from mutagen.mp3 import EasyMP3
from mutagen.easymp4 import EasyMP4

from fuocore.provider import AbstractProvider
from fuocore.utils import log_exectime


logger = logging.getLogger(__name__)


def scan_directory(directory, exts=None, depth=2):
    exts = exts or ['mp3', 'fuo']
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
        if fpath.endswith('mp3') or fpath.endswith('ogg') or fpath.endswith('wma'):
            metadata = EasyMP3(fpath)
        elif fpath.endswith('m4a'):
            metadata = EasyMP4(fpath)
    except MutagenError as e:
        logger.exception('Mutagen parse metadata failed, ignore.')
        return None

    schema = EasyMP3MetadataSongSchema(strict=True)
    metadata_dict = dict(metadata)
    for key in metadata.keys():
        metadata_dict[key] = metadata_dict[key][0]
    if 'title' not in metadata_dict:
        title = fpath.rsplit('/')[-1].split('.')[0]
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


class Scanner:
    """本地歌曲扫描器"""

    DEFAULT_MUSIC_FOLDER = os.path.expanduser('~') + '/Music'

    def __init__(self, paths=None, depth=2):
        self._songs = []
        self.depth = depth
        self.paths = paths or [Scanner.DEFAULT_MUSIC_FOLDER]

    @property
    def songs(self):
        return self._songs

    @log_exectime
    def run(self):
        """scan media files in all paths
        """
        song_exts = ['mp3', 'ogg', 'wma', 'm4a']
        exts = song_exts
        depth = self.depth if self.depth <= 3 else 3
        media_files = []
        for directory in self.paths:
            logger.debug('正在扫描目录(%s)...', directory)
            media_files.extend(scan_directory(directory, exts, depth))

        self._songs = []
        for fpath in media_files:
            song = create_song(fpath)
            if song is not None:
                self._songs.append(song)
            else:
                logger.warning('%s can not be recognized', fpath)
        logger.debug('扫描到 %d 首歌曲', len(self._songs))


class DataBase:
    def __init__(self):
        #: identifier song map: {id: song, ...}
        self._songs = dict()

        #: identifier album map: {id: album, ...}
        self._albums = dict()

        #: identifier artist map: {id: artist, ...}
        self._artists = dict()

    @property
    def songs(self):
        return self._songs.values()

    @property
    def albums(self):
        return self._albums.values()

    @property
    def artists(self):
        return self._artists.values()

    def run(self, songs):
        self._songs.clear()
        self._albums.clear()
        self._artists.clear()

        self.setup_library(songs)
        self.analyze_library()

    def setup_library(self, scanner_songs):
        for song in scanner_songs:
            if song.identifier in self._songs:
                continue
            self._songs[song.identifier] = song

            if song.album is not None:
                album = song.album
                if album.identifier not in self._albums:
                    album_data = {'identifier': album.identifier,
                                  'name': album.name,
                                  'artists_name': album.artists[0].name if album.artists else '',
                                  'songs': []}
                    self._albums[album.identifier], _ = LocalAlbumSchema(strict=True).load(album_data)
                self._albums[album.identifier].songs.append(song)

            if song.artists is not None:
                for artist in song.artists:
                    if artist.identifier not in self._artists:
                        artist_data = {'identifier': artist.identifier,
                                       'name': artist.name,
                                       'songs': [],
                                       'albums': []}
                        self._artists[artist.identifier], _ = LocalArtistSchema(strict=True).load(artist_data)
                    self._artists[artist.identifier].songs.append(song)

    def analyze_library(self):
        for album in self._albums.values():
            try:
                album.songs.sort(key=lambda x: (int(x.disc.split('/')[0]), int(x.track.split('/')[0])))
            except Exception as e:
                logger.exception('Sort album songs failed.')

            if album.artists is not None:
                album_artist = album.artists[0]
                if album_artist.identifier not in self._artists:
                    album_artist_data = {'identifier': album_artist.identifier,
                                         'name': album_artist.name,
                                         'songs': [],
                                         'albums': []}
                    self._artists[album_artist.identifier], _ = LocalArtistSchema(strict=True).load(album_artist_data)
                self._artists[album_artist.identifier].albums.append(album)

        for artist in self._artists.values():
            if artist.albums:
                artist.albums.sort(key=lambda x: (x.songs[0].date is None, x.songs[0].date), reverse=True)
            if artist.songs:
                artist.songs.sort(key=lambda x: x.title)


class LocalProvider(AbstractProvider):

    def __init__(self):
        super().__init__()

        self.library = DataBase()
        self._songs = []
        self._albums = []
        self._artists = []

    def scan(self, paths=None, depth=3):
        scanner = Scanner(paths or [], depth=depth)
        scanner.run()

        self.library.run(scanner.songs)
        self._songs = list(self.library.songs)
        self._albums = list(self.library.albums)
        self._artists = list(self.library.artists)

    @property
    def identifier(self):
        return 'local'

    @property
    def name(self):
        return '本地音乐'

    @property
    def songs(self):
        return self._songs

    @property
    def artists(self):
        return self._artists

    @property
    def albums(self):
        return self._albums

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
        return LSearchModel(q=keyword, songs=result_songs)


provider = LocalProvider()

from .schemas import LocalAlbumSchema
from .schemas import LocalArtistSchema
from .schemas import EasyMP3MetadataSongSchema
from .models import LSearchModel
