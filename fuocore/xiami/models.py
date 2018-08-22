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
    UserModel,
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
        if data is None:
            return None
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
    _detail_fields = ('songs', 'artists', 'desc')

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
    class Meta:
        fields = ('uid', )

    @classmethod
    def get(cls, identifier):
        # FIXME: 获取所有歌曲，而不仅仅是前 100 首
        data = cls._api.playlist_detail(identifier)
        if data is None:
            return None

        schema = PlaylistSchema(strict=True)
        playlist, _ = schema.load(data)
        return playlist

    def add(self, song_id, **kwargs):
        rv = self._api.update_playlist_song(song_id, self.identifier, 'add')
        if rv:
            song = XSongModel.get(song_id)
            self.songs.append(song)
            return True
        return rv

    def remove(self, song_id, allow_not_exist=True):
        rv = self._api.update_playlist_song(song_id, self.identifier, 'del')
        # XXX: make it O(1) if you want
        for song in self.songs:
            if song.identifier == song_id:
                self.songs.remove(song)
        return rv


class XSearchModel(SearchModel, XBaseModel):
    pass


class XUserModel(UserModel, XBaseModel):
    class Meta:
        fields = ('access_token', )

    @classmethod
    def get(cls, identifier):
        user_data = cls._api.user_detail(identifier)
        if user_data is None:
            return None
        schema = UserSchema(strict=True)
        user, _ = schema.load(user_data)
        return user

    @property
    def playlists(self):
        """获取用户创建的歌单

        如果不是用户本人，则不能获取用户默认精选集
        """
        if self._playlists is None:
            self._playlists = []
            schema = PlaylistSchema(strict=True)
            playlists_data = self._api.user_playlists(self.identifier)
            if not playlists_data:
                return
            for playlist_data in playlists_data:
                playlist = schema.load(playlist_data)
                self._playlists.append(playlist)
        return self._playlists

    @playlists.setter
    def playlists(self, value):
        self._playlists = value

    @property
    def fav_playlists(self):
        if self._fav_playlists is None:
            self._fav_playlists = []
            schema = PlaylistSchema(strict=True)
            playlists_data = self._api.user_fav_playlists(self.identifier)
            if not playlists_data:
                return
            for playlist_data in playlists_data:
                playlist = schema.load(playlist_data)
                self._fav_playlists.append(playlist)
        return self._fav_playlists

    @fav_playlists.setter
    def fav_playlists(self, value):
        self._fav_playlists = value


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
    UserSchema,
)  # noqa
