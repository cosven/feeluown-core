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
    UserModel,
    BillboardModel,
    RecommendationModel,
    SearchModel,
)

from .provider import provider

logger = logging.getLogger(__name__)
MUSIC_LIBRARY_PATH = os.path.expanduser('~') + '/Music'


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
    class Meta:
        fields = ('file',)

    @classmethod
    def get(cls, identifier):
        song_data = cls._api.song_detail(int(identifier))
        album = XAlbumModel(identifier=song_data['albumId'],
                            source=provider.identifier,
                            name=song_data['albumName'])
        artists = []
        artist = XArtistModel(identifier=song_data['artistId'],
                              source=provider.identifier,
                              name=song_data['artistName'])
        artists.append(artist)
        song = XSongModel(identifier=song_data['songId'],
                          source=provider.identifier,
                          file=song_data['listenFiles'],
                          title=song_data['songName'],
                          duration=int(song_data['length']),
                          album=album,
                          artists=artists)
        return song

    @classmethod
    def list(cls, identifiers):
        songs_data = cls._api.songs_detail(identifiers)
        songs = []
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            artist = XArtistModel(identifier=song_data['artistId'],
                                  source=provider.identifier,
                                  name=song_data['artistName'])
            artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def _refresh_url(self):
        """刷新获取 url，失败的时候返回空而不是 None"""
        songs = self._api.songs_url([self.file])
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

    # NOTE: if we want to override mode attribute, we must
    # implement both getter and setter.
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
        self._lyric = LyricModel(
            identifier=self.identifier,
            source=self.source,
            content=lyric_data
        )
        return self._lyric

    @lyric.setter
    def lyric(self, value):
        self._lyric = value

    @property
    def comments(self):
        comments_data = self._api.song_comments(self.identifier)
        self._comments = []
        if 'hotList' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotList']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['userId'],
                                   content=comment_data['message'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    def similar_songs(self):
        songs = []
        songs_data = self._api.similar_songs(self.identifier)
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def similar_playlists(self):
        playlists = []
        playlists_data = self._api.similar_playlists(self.identifier)
        for playlist_data in playlists_data:
            playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                      source=provider.identifier,
                                      uid=playlist_data['userId'],
                                      name=playlist_data['collectName'],
                                      cover=playlist_data['collectLogo'])
            playlists.append(playlist)
        return playlists

    def set_favorite(self, allow_exist=True):
        return self._api.update_favorite_song(self.identifier, 'add')

    def cancel_favorite(self, allow_exist=True):
        return self._api.update_favorite_song(self.identifier, 'del')

    def set_trash(self, allow_exist=True):
        return self._api.update_fm_trash(self.identifier, 'add')

    def cancel_trash(self, allow_exist=True):
        return self._api.update_fm_trash(self.identifier, 'del')


class XAlbumModel(AlbumModel, XBaseModel):
    _detail_fields = ('cover', 'songs', 'artists')

    @classmethod
    def get(cls, identifier):
        album_data = cls._api.album_detail(identifier)
        if album_data is None:
            return None

        songs = []
        for song_data in album_data['songs']:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)

        artists = []
        for artist_data in album_data['artists']:
            artist = XArtistModel(identifier=artist_data['artistId'],
                                  source=provider.identifier,
                                  name=artist_data['artistName'])
            artists.append(artist)

        album = XAlbumModel(identifier=album_data['albumId'],
                            source=provider.identifier,
                            name=album_data['albumName'],
                            cover=album_data['albumLogo'],
                            songs=songs,
                            artists=artists,
                            desc=album_data['description'])
        return album

    @property
    def comments(self):
        comments_data = self._api.album_comments(self.identifier)
        self._comments = []
        if 'hotList' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotList']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['userId'],
                                   content=comment_data['message'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value


class XArtistModel(ArtistModel, XBaseModel):
    _detail_fields = ('cover', 'songs', 'albums')

    @classmethod
    def get(cls, identifier):
        _artist_data = cls._api.artist_detail(identifier)
        if _artist_data is None:
            return None

        songs_data, _ = cls._api.artist_songs(identifier)
        songs = []
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)

        albums_data, _ = cls._api.artist_albums(identifier)
        albums = []
        for album_data in albums_data:
            album = XAlbumModel(identifier=album_data['albumId'],
                                source=provider.identifier,
                                name=album_data['albumName'])
            albums.append(album)

        artist = XArtistModel(identifier=_artist_data['artistId'],
                              source=provider.identifier,
                              name=_artist_data['artistName'],
                              cover=_artist_data['artistLogo'],
                              songs=songs,
                              albums=albums,
                              desc=_artist_data['description'])
        return artist

    @property
    def comments(self):
        comments_data = self._api.artist_comments(self.identifier)
        self._comments = []
        if 'hotList' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotList']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['userId'],
                                   content=comment_data['message'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    def similar_artists(self):
        artists = []
        artists_data = self._api.similar_artists(self.identifier)
        for artist_data in artists_data:
            artist = XArtistModel(identifier=artist_data['artistId'],
                                  source=provider.identifier,
                                  name=artist_data['artistName'],
                                  cover=artist_data['artistLogo'])
            artists.append(artist)
        return artists


class XPlaylistModel(PlaylistModel, XBaseModel):
    # 默认url:http://pic.xiami.net/images/album/img30/130/5abb2bc0ac13c_6525430_1522215872.png
    _detail_fields = ('cover', 'songs')

    class Meta:
        fields = ('uid',)

    @classmethod
    def get(cls, identifier):
        playlist_data = cls._api.playlist_detail(identifier)
        if playlist_data is None:
            return None

        songs = []
        for song_data in playlist_data['songs']:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)

        playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                  source=provider.identifier,
                                  uid=playlist_data['userId'],
                                  name=playlist_data['collectName'],
                                  cover=playlist_data['collectLogo'],
                                  songs=songs,
                                  desc=playlist_data['description'])
        return playlist

    @property
    def comments(self):
        comments_data = self._api.playlist_comments(self.identifier)
        self._comments = []
        if 'hotList' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotList']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['userId'],
                                   content=comment_data['message'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    @classmethod
    def create(cls, user_id, name='default'):
        playlist_data = cls._api.new_playlist(name)
        playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                  source=provider.identifier,
                                  uid=user_id,
                                  name=name)
        return playlist

    def rename(self, name):
        return self._api.update_playlist_name(self.identifier, name)

    def delete(self):
        return self._api.delete_playlist(self.identifier)

    def add(self, song_id, allow_exist=True):
        for song in self.songs:
            if song.identifier == song_id:
                return False
        rv = self._api.update_playlist_song(self.identifier, song_id, 'add')
        if True:
            song = XSongModel.get(song_id)
            self.songs.append(song)
        return rv

    def remove(self, song_id, allow_not_exist=True):
        for song in self.songs:
            if song.identifier == song_id:
                rv = self._api.update_playlist_song(self.identifier, song_id, 'del')
                if rv:
                    self.songs.remove(song)
                    return True
                return rv
        return False


class XUserModel(UserModel, XBaseModel):
    _detail_fields = ('playlists', 'fav_songs', 'fav_albums', 'fav_artists', 'fav_playlists')

    def _get_playlists(self):
        playlists_data, _info = self._api.user_playlists(self.identifier, limit=200)
        while _info['more']:
            _playlists, _info = self._api.user_playlists(self.identifier, _info['next'], 200)
            playlists_data.extent(_playlists)
        playlists = []
        for playlist_data in playlists_data:
            playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                      source=provider.identifier,
                                      uid=playlist_data['userId'],
                                      name=playlist_data['collectName'],
                                      cover=playlist_data['collectLogo'])
            playlists.append(playlist)
        return playlists

    def _get_fav_songs(self):
        fav_songs_data, _info = self._api.user_favorite_songs(self.identifier, limit=200)
        while _info['more']:
            _fav_songs, _info = self._api.user_favorite_songs(self.identifier, _info['next'], 200)
            fav_songs_data.extend(_fav_songs)
        songs = []
        for song_data in fav_songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def _get_fav_albums(self):
        fav_albums_data, _info = self._api.user_favorite_albums(self.identifier, limit=200)
        while _info['more']:
            _fav_albums, _info = self._api.user_favorite_albums(self.identifier, _info['next'], 200)
            fav_albums_data.extend(_fav_albums)
        fav_albums = []
        for album_data in fav_albums_data:
            album = XAlbumModel(identifier=album_data['albumId'],
                                source=provider.identifier,
                                name=album_data['albumName'],
                                cover=album_data['albumLogo'])
            fav_albums.append(album)
        return fav_albums

    def _get_fav_artists(self):
        fav_artists_data, _info = self._api.user_favorite_artists(self.identifier, limit=200)
        while _info['more']:
            _fav_artists, _info = self._api.user_favorite_artists(self.identifier, _info['next'], 200)
            fav_artists_data.extend(_fav_artists)
        fav_artists = []
        for artist_data in fav_artists_data:
            artist = XArtistModel(identifier=artist_data['artistId'],
                                  source=provider.identifier,
                                  name=artist_data['artistName'],
                                  cover=artist_data['artistLogo'])
            fav_artists.append(artist)
        return fav_artists

    def _get_fav_playlists(self):
        fav_playlists_data, _info = self._api.user_favorite_playlists(self.identifier, limit=200)
        while _info['more']:
            _fav_playlists, _info = self._api.user_favorite_playlists(self.identifier, _info['next'], 200)
            fav_playlists_data.extend(_fav_playlists)
        fav_playlists = []
        for playlist_data in fav_playlists_data:
            playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                      source=provider.identifier,
                                      uid=playlist_data['userId'],
                                      name=playlist_data['collectName'],
                                      cover=playlist_data['collectLogo'])
            fav_playlists.append(playlist)
        return fav_playlists

    @classmethod
    def get(cls, identifier):
        user_detail = cls._api.user_detail(identifier)
        user = XUserModel(identifier=identifier,
                          source=provider.identifier,
                          name=user_detail['nickName'],
                          cover=user_detail['avatar'].split('@')[0],
                          cookies=cls._api.cookies)
        user.playlists = user._get_playlists()
        user.fav_songs = user._get_fav_songs()
        user.fav_albums = user._get_fav_albums()
        user.fav_artists = user._get_fav_artists()
        user.fav_playlists = user._get_fav_playlists()
        return user

    def fm_songs(self):
        songs_data = self._api.personal_fm()
        songs = []
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def recommend_songs(self):
        songs_data = self._api.recommend_songs()
        songs = []
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return songs

    def recommend_playlists(self):
        playlists_data = self._api.recommend_playlists()
        playlists = []
        for playlist_data in playlists_data:
            playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                      source=provider.identifier,
                                      uid=playlist_data['userId'],
                                      name=playlist_data['collectName'],
                                      cover=playlist_data['collectLogo'])
            playlists.append(playlist)
        return playlists


class XBillboardModel(BillboardModel, XBaseModel):
    _detail_fields = ('t', 'cover', 'songs')

    @classmethod
    def get(cls, identifier):
        songs_data = cls._api.top_songlist(identifier['id'])
        songs = []
        for song_data in songs_data:
            album = XAlbumModel(identifier=song_data['albumId'],
                                source=provider.identifier,
                                name=song_data['albumName'])
            artists = []
            for artist_data in song_data['singerVOs']:
                artist = XArtistModel(identifier=artist_data['artistId'],
                                      source=provider.identifier,
                                      name=artist_data['artistName'])
                artists.append(artist)
            song = XSongModel(identifier=song_data['songId'],
                              source=provider.identifier,
                              file=song_data['listenFiles'],
                              title=song_data['songName'],
                              duration=int(song_data['length']),
                              album=album,
                              artists=artists)
            songs.append(song)
        return XBillboardModel(source=provider.identifier,
                               t=identifier['name'],
                               # cover=songs[0].album.cover,
                               songs=songs)

    @staticmethod
    def dicts():
        items = []
        for item in provider.api.return_toplists():
            items.append({'id': item['billboardId'],
                          'name': item['name']})
        return items


class XRecommendationModel(RecommendationModel, XBaseModel):
    _detail_fields = ('r', 'playlists')

    @classmethod
    def get(cls, identifier):
        playlists_data, _ = cls._api.top_playlists(identifier)
        playlists = []
        for playlist_data in playlists_data:
            playlist = XPlaylistModel(identifier=playlist_data['listId'],
                                      source=provider.identifier,
                                      uid=playlist_data['userId'],
                                      name=playlist_data['collectName'],
                                      cover=playlist_data['collectLogo'])
            playlists.append(playlist)
        return XRecommendationModel(source=provider.identifier,
                                    r=identifier,
                                    playlists=playlists)

    @staticmethod
    def dicts():
        items = []
        for items_data in provider.api.return_playlist_classes():
            items.append({'classes': items_data['title'],
                          'items': [item_data['name'] for item_data in items_data['items']]})
        return items


class XSearchModel(SearchModel, XBaseModel):
    pass


def search(keyword, **kwargs):
    songs_data, _ = provider.api.search(keyword)
    songs = []
    for song_data in songs_data:
        album = XAlbumModel(identifier=song_data['albumId'],
                            source=provider.identifier,
                            name=song_data['albumName'])
        artists = []
        artist = XArtistModel(identifier=song_data['artistId'],
                              source=provider.identifier,
                              name=song_data['artistName'])
        artists.append(artist)
        song = XSongModel(identifier=song_data['songId'],
                          source=provider.identifier,
                          file=song_data['listenFiles'],
                          title=song_data['songName'],
                          duration=int(song_data['length']),
                          album=album,
                          artists=artists)
        songs.append(song)
    return XSearchModel(source=provider.identifier,
                        q=keyword,
                        songs=songs)
