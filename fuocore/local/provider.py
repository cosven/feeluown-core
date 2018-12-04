# -*- coding: utf-8 -*-

"""
TODO: 这个模块中目前逻辑非常多，包括音乐目录扫描、音乐库的构建等小部分，
这些小部分理论都可以从中拆除。
"""

import copy
import logging
import os

from fuzzywuzzy import process
from marshmallow.exceptions import ValidationError
from mutagen import MutagenError
from mutagen.mp3 import EasyMP3
from mutagen.easymp4 import EasyMP4

from fuocore.provider import AbstractProvider
from fuocore.utils import log_exectime


logger = logging.getLogger(__name__)
MUSIC_LIBRARY_PATH = os.path.expanduser('~') + '/Music'


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
        logger.error('Mutagen parse metadata failed, ignore.')
        logger.debug(str(e))
        return None

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


@log_exectime
def scan(paths, depth=2):
    """scan media files in all paths
    """
    song_exts = ['mp3', 'ogg', 'wma', 'm4a']
    exts = song_exts
    depth = depth if depth <= 3 else 3
    media_files = []
    for directory in paths:
        logger.debug('正在扫描目录(%s)...', directory)
        media_files.extend(scan_directory(directory, exts, depth))
    songs = []
    for fpath in media_files:
        song = create_song(fpath)
        if song is not None:
            songs.append(song)
        else:
            logger.warning('%s can not be recognized', fpath)
    logger.debug('扫描到 %d 首歌曲', len(songs))
    return songs


class Scanner:
    def __init__(self, paths=None, depth=2):
        self.__songs = []

        #: identifier song map: {id: song, ...}
        self._songs = dict()

        #: identifier album map: {id: album, ...}
        self._albums = dict()

        #: identifier artist map: {id: artist, ...}
        self._artists = dict()

        #: music resource paths to be scanned, list
        self.depth = depth
        self.paths = paths or [MUSIC_LIBRARY_PATH]

    @property
    def songs(self):
        return self._songs.values()

    @property
    def albums(self):
        return self._albums.values()

    @property
    def artists(self):
        return self._artists.values()

    def run(self):
        self.__songs = scan(self.paths, self.depth)
        self.setup_library()

    @log_exectime
    def setup_library(self):
        # FIXME: 函数太长，请重构我！
        self._songs.clear()
        self._albums.clear()
        self._artists.clear()

        for song in self.__songs:
            if song.identifier in self._songs:
                continue
            self._songs[song.identifier] = song
            # 增加ablum.songs的信息
            if song.album is not None:
                album = song.album
                if album.identifier not in self._albums:
                    import copy
                    self._albums[album.identifier] = copy.deepcopy(album)
                    self._albums[album.identifier].songs = [song]
                else:
                    self._albums[album.identifier].songs.append(song)
            # 增加artist.songs的信息
            if song.artists is not None:
                for artist in song.artists:
                    if artist.identifier not in self._artists:
                        self._artists[artist.identifier] = copy.deepcopy(artist)
                        self._artists[artist.identifier].albums = []
                        self._artists[artist.identifier].songs = [song]
                    else:
                        self._artists[artist.identifier].songs.append(song)

        # 更新专辑歌曲排序,更新艺术家专辑信息,更新歌曲专辑信息
        for album in self._albums.values():
            # 增加artists.albums, 必须在这里进行(如果在song中进行会导致artist.albums重复)
            if album.artists:
                # 专辑艺术家只能有一个!
                album_artist = album.artists[0]
                if album_artist.identifier not in self._artists:
                    self._artists[album_artist.identifier] = copy.deepcopy(album_artist)
                    self._artists[album_artist.identifier].albums = [album]
                    self._artists[album_artist.identifier].songs = []
                else:
                    self._artists[album_artist.identifier].albums.append(album)
        for artist in self._artists.values():
            # if artist.albums:
            #     artist.albums.sort(key=lambda x: (x.songs[0].date is None, x.songs[0].date), reverse=True)
            if artist.songs:
                artist.songs.sort(key=lambda x: x.title)


class LocalProvider(AbstractProvider):

    def __init__(self):
        super().__init__()

        self._identifier_song_map = dict()
        self._identifier_album_map = dict()
        self._identifier_artist_map = dict()
        self._songs = []
        self._albums = []
        self._artists = []

    def scan(self, paths=None, depth=2):
        scanner = Scanner(paths or [], depth=depth)
        scanner.run()
        self._identifier_song_map = scanner._songs
        self._identifier_album_map = scanner._albums
        self._identifier_artist_map = scanner._artists
        self._songs = list(scanner.songs)
        self._albums = list(scanner.albums)
        self._artists = list(scanner.artists)

    @property
    def identifier(self):
        return 'local'

    @property
    def name(self):
        return '本地音乐'

    @property
    def identifier_song_map(self):
        return self._identifier_song_map

    @property
    def identifier_artist_map(self):
        return self._identifier_artist_map

    @property
    def identifier_album_map(self):
        return self._identifier_album_map

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


from fuocore.local.schemas import EasyMP3MetadataSongSchema
from .models import LSearchModel
