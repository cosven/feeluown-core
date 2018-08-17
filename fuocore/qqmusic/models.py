import logging
import time
import os

from fuocore.models import (
    BaseModel,
    SongModel,
    AlbumModel,
    ArtistModel,
    PlaylistModel,
    LyricModel,
    CommentModel,
    BillboardModel,
    RecommendationModel,
    UserModel,
    SearchModel,
)

from .provider import provider

logger = logging.getLogger(__name__)
MUSIC_LIBRARY_PATH = os.path.expanduser('~') + '/Music'


class QBaseModel(BaseModel):
    # FIXME: remove _detail_fields and _api to Meta
    _detail_fields = ()
    _api = provider.api

    class Meta:
        allow_get = True
        provider = provider

    def __getattribute__(self, name):
        cls = type(self)
        value = object.__getattribute__(self, name)
        if name in cls._detail_fields and not value:
            logger.debug('Field %s value is None, get model detail first.' % name)
            obj = cls.get(self.identifier)
            for field in cls._detail_fields:
                setattr(self, field, getattr(obj, field))
            value = object.__getattribute__(self, name)
        elif name in cls._detail_fields and not value:
            logger.warning('Field %s value is not None, but is %s' % (name, value))
        return value


class QSongModel(SongModel, QBaseModel):
    class Meta:
        fields = ('mid',)

    @classmethod
    def get(cls, identifier):
        song_data = cls._api.song_detail(identifier)
        album = QAlbumModel(identifier=song_data['album']['mid'],
                            source=provider.identifier,
                            name=song_data['album']['name'])
        artists = []
        for artist_data in song_data['singer']:
            artist = QArtistModel(identifier=artist_data['id'],
                                  source=provider.identifier,
                                  name=artist_data['name'])
            artists.append(artist)
        song = QSongModel(identifier=song_data['mid'],
                          source=provider.identifier,
                          mid=song_data['file']['media_mid'],
                          title=song_data['name'],
                          duration=song_data['interval'] * 1000,
                          album=album,
                          artists=artists)
        return song

    @classmethod
    def list(cls, identifiers):
        songs = []
        for identifier in identifiers:
            song_data = cls._api.song_detail(identifier)
            album = QAlbumModel(identifier=song_data['album']['mid'],
                                source=provider.identifier,
                                name=song_data['album']['name'])
            artists = []
            for artist_data in song_data['singer']:
                artist = QArtistModel(identifier=artist_data['id'],
                                      source=provider.identifier,
                                      name=artist_data['name'])
                artists.append(artist)
            song = QSongModel(identifier=song_data['mid'],
                              source=provider.identifier,
                              mid=song_data['file']['media_mid'],
                              title=song_data['name'],
                              duration=song_data['interval'] * 1000,
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def _refresh_url(self):
        """刷新获取 url，失败的时候返回空而不是 None"""
        songs = self._api.songs_url([self.mid])
        if songs and songs[0]:
            self.url = songs[0]
        else:
            self.url = self._find_in_3rd() or ''

    def _find_in_3rd(self):
        logger.debug('try to find {} equivalent in 3rd'.format(self))
        return self._api.get_3rd_url(title=self.title,
                                     artist_name=self.artists_name,
                                     duration=self.duration)

    def _find_in_local(self):
        path = os.path.join(MUSIC_LIBRARY_PATH, self.filename)
        if os.path.exists(path):
            logger.debug('find local file for {}'.format(self))
            return path
        return None

    @property
    def url(self):
        local_path = self._find_in_local()
        if local_path:
            return local_path

        if not self._url:
            self._refresh_url()
        elif time.time() > self._expired_at:
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
            assert isinstance(self._lyric, LyricModel)
            return self._lyric
        lyric_data = self._api.song_lyrics(self.identifier)
        self._lyric = LyricModel(identifier=self.identifier,
                                 source=self.source,
                                 content=lyric_data)
        return self._lyric

    @lyric.setter
    def lyric(self, value):
        self._lyric = value

    # @property
    # def comments(self):
    #     self._comments = []
    #     return self._comments
    #
    # @comments.setter
    # def comments(self, value):
    #     self._comments = value


class QAlbumModel(AlbumModel, QBaseModel):
    _detail_fields = ('cover', 'songs', 'artists')

    @classmethod
    def get(cls, identifier):
        album_data = cls._api.album_detail(identifier)
        if album_data is None:
            return None

        songs = []
        for song_data in album_data['list']:
            album = QAlbumModel(identifier=song_data['albummid'],
                                source=provider.identifier,
                                name=song_data['albumname'])
            artists = []
            for artist_data in song_data['singer']:
                artist = QArtistModel(identifier=artist_data['mid'],
                                      source=provider.identifier,
                                      name=artist_data['name'])
                artists.append(artist)
            song = QSongModel(identifier=song_data['songmid'],
                              source=provider.identifier,
                              mid=song_data['strMediaMid'],
                              title=song_data['songname'],
                              duration=song_data['interval'] * 1000,
                              album=album,
                              artists=artists)
            songs.append(song)

        artists = []
        artist = QArtistModel(identifier=album_data['singermid'],
                              source=provider.identifier,
                              name=album_data['singername'])
        artists.append(artist)

        album = QAlbumModel(identifier=album_data['mid'],
                            source=provider.identifier,
                            name=album_data['name'],
                            cover='http://imgcache.qq.com/music/photo/mid_album_300/{}/{}/{}.jpg'.format(
                                identifier[-2], identifier[-1], identifier),
                            songs=songs,
                            artists=artists,
                            desc=album_data['desc'])
        return album

    # @property
    # def comments(self):
    #     self._comments = []
    #     return self._comments
    #
    # @comments.setter
    # def comments(self, value):
    #     self._comments = value


class QArtistModel(ArtistModel, QBaseModel):
    _detail_fields = ('cover', 'songs', 'albums')

    @classmethod
    def get(cls, identifier):
        _artist_data, _ = cls._api.artist_detail(identifier)
        if _artist_data is None:
            return None

        songs = []
        for song_data in _artist_data['list']:
            album = QAlbumModel(identifier=song_data['musicData']['albummid'],
                                source=provider.identifier,
                                name=song_data['musicData']['albumname'])
            artists = []
            for artist_data in song_data['musicData']['singer']:
                artist = QArtistModel(identifier=artist_data['mid'],
                                      source=provider.identifier,
                                      name=artist_data['name'])
                artists.append(artist)
            song = QSongModel(identifier=song_data['musicData']['songmid'],
                              source=provider.identifier,
                              mid=song_data['musicData']['strMediaMid'],
                              title=song_data['musicData']['songname'],
                              duration=song_data['musicData']['interval'] * 1000,
                              album=album,
                              artists=artists)
            songs.append(song)

        albums_data, _ = cls._api.artist_albums(identifier)
        albums = []
        for album_data in albums_data:
            album = QAlbumModel(identifier=album_data['albumMID'],
                                source=provider.identifier,
                                name=album_data['albumName'])
            albums.append(album)

        artist = QArtistModel(identifier=_artist_data['singer_mid'],
                              source=provider.identifier,
                              name=_artist_data['singer_name'],
                              cover='http://imgcache.qq.com/music/photo/mid_singer_300/{}/{}/{}.jpg'.format(
                                  identifier[-2], identifier[-1], identifier),
                              songs=songs,
                              albums=albums,
                              desc=_artist_data['SingerDesc'])
        return artist

    # @property
    # def comments(self):
    #     self._comments = []
    #     return self._comments
    #
    # @comments.setter
    # def comments(self, value):
    #     self._comments = value


class QPlaylistModel(PlaylistModel, QBaseModel):
    _detail_fields = ('cover', 'songs')

    @classmethod
    def get(cls, identifier):
        playlist_data = cls._api.playlist_detail(identifier)
        if playlist_data is None:
            return None

        songs = []
        for song_data in playlist_data['songlist']:
            album = QAlbumModel(identifier=song_data['albummid'],
                                source=provider.identifier,
                                name=song_data['albumname'])
            artists = []
            for artist_data in song_data['singer']:
                artist = QArtistModel(identifier=artist_data['mid'],
                                      source=provider.identifier,
                                      name=artist_data['name'])
                artists.append(artist)
            song = QSongModel(identifier=song_data['songmid'],
                              source=provider.identifier,
                              mid=song_data['strMediaMid'],
                              title=song_data['songname'],
                              duration=song_data['interval'] * 1000,
                              album=album,
                              artists=artists)
            songs.append(song)

        playlist = QPlaylistModel(identifier=playlist_data['disstid'],
                                  source=provider.identifier,
                                  name=playlist_data['dissname'],
                                  cover=playlist_data['logo'],
                                  songs=songs,
                                  desc=playlist_data['desc'])
        return playlist

    # @property
    # def comments(self):
    #     self._comments = []
    #     return self._comments
    #
    # @comments.setter
    # def comments(self, value):
    #     self._comments = value


class QUserModel(UserModel, QBaseModel):  # QQ音乐此功能不完善
    _detail_fields = ('playlists', 'fav_songs', 'fav_albums', 'fav_artists', 'fav_playlists')

    # @classmethod
    # def get(cls, identifier):
    #     user = QUserModel(identifier=identifier,
    #                       source=provider.identifier,
    #                       cookies=cls._api.cookies)
    #     return user


class QBillboardModel(BillboardModel, QBaseModel):
    pass


class QRecommendationModel(RecommendationModel, QBaseModel):
    pass


class QSearchModel(SearchModel, QBaseModel):
    pass


def search(keyword, **kwargs):
    songs_data, _ = provider.api.search(keyword)
    songs = []
    for song_data in songs_data:
        if song_data['songid'] is not 0:
            album = QAlbumModel(identifier=song_data['albummid'],
                                source=provider.identifier,
                                name=song_data['albumname'])
            artists = []
            for artist_data in song_data['singer']:
                artist = QArtistModel(identifier=artist_data['mid'],
                                      source=provider.identifier,
                                      name=artist_data['name'])
                artists.append(artist)
            song = QSongModel(identifier=song_data['songmid'],
                              source=provider.identifier,
                              mid=song_data['media_mid'],
                              title=song_data['songname'],
                              duration=song_data['interval'] * 1000,
                              album=album,
                              artists=artists)
            songs.append(song)
    return QSearchModel(source=provider.identifier,
                        q=keyword,
                        songs=songs)
