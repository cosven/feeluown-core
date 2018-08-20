import logging
import time

from fuocore.models import (
    BaseModel,
    SongModel,
    AlbumModel,
    ArtistModel,
    PlaylistModel,
    LyricModel,
    SearchModel,
)

from .provider import provider

logger = logging.getLogger(__name__)


class XBaseModel(BaseModel):
    # FIXME: remove _detail_fields and _api to Meta
    _detail_fields = ()
    _api = provider.api

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


class XSongModel(SongModel, XBaseModel):

    @classmethod
    def get(cls, identifier):
        data = cls._api.song_detail(identifier)
        schema = SongSchema(strict=True)
        song, _ = schema.load(data)
        return song

    def _refresh_url(self):
        song = self.get(self.identifier)
        self.url = song.url

    @property
    def url(self):
        if time.time() > self._expired_at:
            logger.debug('song({}) url is expired, refresh...'.format(self))
            self._refresh_url()
        return self._url

    @url.setter
    def url(self, value):
        self._expired_at = time.time() + 60 * 60 * 1  # one hour
        self._url = value

    @property
    def lyric(self):
        if self._lyric is not None:
            return self._lyric
        content = self._api.song_lyric(self.identifier)
        self.lyric = LyricModel(
            identifier=self.identifier,
            source=self.source,
            content=content
        )
        return self._lyric

    @lyric.setter
    def lyric(self, value):
        self._lyric = value


class XAlbumModel(AlbumModel, XBaseModel):
    _detail_fields = ('artists', )

    @classmethod
    def get(cls, identifier):
        data = cls._api.album_detail(identifier)
        if data is None:
            return None

        schema = AlbumSchema(strict=True)
        album, _ = schema.load(data)
        return album


class XArtistModel(ArtistModel, XBaseModel):
    _detail_fields = ('cover', 'desc')

    @classmethod
    def get(cls, identifier):
        data = cls._api.artist_detail(identifier)
        if data is None:
            return None

        schema = ArtistSchema(strict=True)
        artist, _ = schema.load(data)
        return artist

    @property
    def songs(self):
        if self._songs is None:
            self._songs = []
            data_songs = self._api.artist_songs(self.identifier) or []
            if data_songs:
                schema = NestedSongSchema(strict=True)
                for data_song in data_songs:
                    song, _ = schema.load(data_song)
                    self._songs.append(song)
        return self._songs

    @songs.setter
    def songs(self, value):
        self._songs = value


class XPlaylistModel(PlaylistModel, XBaseModel):
    # 默认url:http://pic.xiami.net/images/album/img30/130/5abb2bc0ac13c_6525430_1522215872.png

    class Meta:
        fields = ('uid',)

    @classmethod
    def get(cls, identifier):
        # FIXME: 获取所有歌曲，而不仅仅是前 100 首
        data = cls._api.playlist_detail(identifier)
        if data is None:
            return None

        schema = PlaylistSchema(strict=True)
        playlist, _ = schema.load(data)
        return playlist


class XSearchModel(SearchModel, XBaseModel):
    pass


def search(keyword, **kwargs):
    data = provider.api.search(keyword, **kwargs)
    schema = SongSearchSchema(strict=True)
    result, _ = schema.load(data)
    result.q = keyword
    return result


from .schemas import (
    AlbumSchema,
    ArtistSchema,
    PlaylistSchema,
    NestedSongSchema,
    SongSchema,
    SongSearchSchema,
)  # noqa
