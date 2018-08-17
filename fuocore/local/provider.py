# -*- coding: utf-8 -*-

import logging
import os

from fuzzywuzzy import process
from marshmallow.exceptions import ValidationError
from mutagen import MutagenError
from mutagen.mp3 import EasyMP3

from fuocore.provider import AbstractProvider
from fuocore.utils import log_exectime

from fuocore.local.schemas import EasyMP3MetadataSongSchema
from fuocore.models import (
    BaseModel, SearchModel, SongModel, AlbumModel, ArtistModel
)

logger = logging.getLogger(__name__)
MUSIC_LIBRARY_PATH = os.path.expanduser('~') + '/Music/本地音乐'
# MUSIC_LIBRARY_PATH = os.path.expanduser('~') + '/PycharmProjects/music_api/data'


def _add_cover(song,metadata):
    HOME_DIR = os.path.expanduser('~') + '/.FeelUOwn'
    CACHE_DIR = HOME_DIR + '/cache'

    def _hash(img_name):
        from hashlib import md5
        pure_url = img_name.split('?')[0]
        return md5(pure_url.encode('utf-8')).hexdigest()

    def _gen_fname(hname):
        import time
        ts_str = str(int(time.time()))
        return hname + '-' + ts_str

    def judge(img_name):
        hname = _hash(img_name)
        for fname in os.listdir(CACHE_DIR):
            if fname.startswith(hname):
                logger.debug('get img cache for %s' % img_name)
                return os.path.join(CACHE_DIR, fname)
        return None

    def create(img_name):
        hname = _hash(img_name)
        fname = _gen_fname(hname)
        logger.debug('create img cache for %s' % img_name)
        return os.path.join(CACHE_DIR, fname)

    if song.album:
        img_name = 'album_' + song.album.identifier
        fpath = judge(img_name)
        if fpath is None:
            fpath = create(img_name)
            try:
                with open(fpath, 'wb') as f:
                    f.write(metadata.tags._EasyID3__id3._DictProxy__dict['APIC:'].data)
            except Exception:
                logger.exception('save image file failed')
        if song.album:
            song.album.cover = img_name
        if song.artists:
            for artist in song.artists:
                artist.cover = img_name
    return song


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

    try:
        song = _add_cover(song, metadata)
    except ValidationError:
        logger.exeception('保存音乐文件({})封面失败'.format(song.filename))
    return song


class LocalProvider(AbstractProvider):
    def __init__(self, library_paths=None, depth=2):
        # TODO: 避免在初始化的时候进行 scan
        self._library_paths = library_paths

        self._songs = []

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
                # 本有更简洁的写法(像原版那样),但那样可能要重复两次循环(第一遍确定map 第二遍更新map中的歌曲艺术家专辑)
                # 所以先这样写着,后面再测试效率,这样的话要给model添加detail_fields,关键词不为空的时候调用get方法
                # 网络的model是否也能先用map再实时更新album_map和artist_map(只有通过model的get方法获得的才加到map中)
                # 举例:如果通过song获得的album加到map中可能会出现信息不完整的情况
                if song.album is not None:
                    if song.album.identifier in self._identifier_album_map.keys():
                        _album = self._identifier_album_map[song.album.identifier]
                    else:
                        _album = song.album
                    if _album.songs:
                        _album.songs.extend([song])
                    else:
                        _album.songs = [song]
                    if _album.artists and song.artists:
                        _album.artists.extend(song.artists)
                    else:
                        _album.artists = song.artists
                    if _album.cover is None:
                        _album.cover = song.album.cover
                    self._identifier_album_map[_album.identifier] = _album
                    song.album = _album
                if song.artists:
                    _artists = []
                    for artist in song.artists:
                        if artist.identifier in self._identifier_artist_map.keys():
                            _artist = self._identifier_artist_map[artist.identifier]
                        else:
                            _artist = artist
                        if _artist.songs:
                            _artist.songs.extend([song])
                        else:
                            _artist.songs = [song]
                        self._identifier_artist_map[_artist.identifier] = _artist
                        _artists.extend([_artist])
                    song.artists = _artists
        # 更新专辑信息:统计合并专辑艺术家和修改专辑歌曲排序
        # 更新艺术家信息:追加艺术家专辑和修改艺术家歌曲排序
        for album in self._identifier_album_map.values():
            if album.artists:
                # 更新专辑艺术家的信息:一张专辑暂定只有一个艺术家
                # 后期将有两种改进(可在软件设置中让用户自由选择!!!!):
                # 1.根据艺术家的分布比例自适应确定艺术家的数量(如果分布较均匀或参与者人数很多则设为Various Artists设为Apple Music中的合辑标志)
                # 2.使用从歌曲内部读取到的'album_artists'信息,这样只有获取艺术家专辑的操作才需要在这部分更新
                _identifiers = [_artist.identifier for _artist in album.artists]
                _identifier_dict = dict(
                    (identifier, _identifiers.count(identifier)) for identifier in set(_identifiers))
                _identifier = sorted(_identifier_dict.items(), key=lambda x: x[1], reverse=True)[0][0]
                album.artists = [self._identifier_artist_map[_identifier]]
                # 对应更新艺术家的专辑数量
                _artist = self._identifier_artist_map[_identifier]
                if _artist.albums:
                    _artist.albums.extend([album])
                else:
                    _artist.albums = [album]
                self._identifier_artist_map[_identifier] = _artist
        # 后续改进:需要cd_num/track_num/publication_time[可能会精确到天也可能粗略到年也可能无信息]
        # 流派信息基本不太完整或千篇一律,是否真的需要(不过大多数音乐软件里都存在按照这个分类!!)
        # 根据cd_num和track_num对专辑歌曲进行排序(若不存在则设为:1 1)
        # 根据年份信息对艺术家专辑进行排序,根据歌曲名(等信息)对艺术家歌曲进行排序
        # 注:艺术家歌曲包括其参与歌曲制作的歌曲,艺术家专辑包括其参数专辑制作的歌曲
        # 注:排序方案在gui或container里也可以做(很多类型的排序功能),但进行预排序会节省时间(如果软件里使用快排的话)
        # 想法:本地音乐库的分析，比如类似ios中ripple player的功能生成推荐歌单啥的

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


class LBaseModel(BaseModel):
    # FIXME: remove _detail_fields and _api to Meta
    _detail_fields = ()

    class Meta:
        allow_get = True
        provider = provider

    def __getattribute__(self, name):
        cls = type(self)
        value = object.__getattribute__(self, name)
        if name in cls._detail_fields and value is None:
            logger.debug('Field %s value is None, get model detail first.' % name)
            obj = cls.get(self.identifier)
            for field in cls._detail_fields:
                setattr(self, field, getattr(obj, field))
            value = object.__getattribute__(self, name)
        elif name in cls._detail_fields and not value:
            logger.warning('Field %s value is not None, but is %s' % (name, value))
        return value


class LSongModel(SongModel, LBaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_song_map.get(identifier)

    @classmethod
    def list(cls, identifiers):
        return map(cls._meta.provider._identifier_song_map.get, identifiers)


class LAlbumModel(AlbumModel, LBaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_album_map.get(identifier)


class LArtistModel(ArtistModel, LBaseModel):
    @classmethod
    def get(cls, identifier):
        return cls._meta.provider._identifier_artist_map.get(identifier)
