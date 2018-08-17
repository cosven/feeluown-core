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


class NBaseModel(BaseModel):
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


class NSongModel(SongModel, NBaseModel):
    @classmethod
    def get(cls, identifier):
        song_data = cls._api.song_detail(int(identifier))
        song, _ = NeteaseSongSchema(strict=True).load(song_data)
        return song

    @classmethod
    def list(cls, identifiers):
        songs_data = cls._api.songs_detail(identifiers)
        songs = []
        for song_data in songs_data:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return songs

    def _refresh_url(self):
        """刷新获取 url，失败的时候返回空而不是 None"""
        songs = self._api.songs_url([int(self.identifier)])
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

    # NOTE: if we want to override model attribute, we must
    # implement both getter and setter.
    @property
    def url(self):
        """
        We will always check if this song file exists in local library,
        if true, we return the url of the local file.
        If a song does not exists in netease library, we will *try* to
        find a equivalent in 3rd temporarily.

        .. note::

            As netease song url will be expired after a period of time,
            we can not use static url here. Currently, we assume that the
            expiration time is 100 seconds, after the url expires, it
            will be automaticly refreshed.
        """
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
        lrc = lyric_data.get('lrc', {})
        lyric = lrc.get('lyric', '')
        self._lyric = LyricModel(identifier=self.identifier,
                                 source=self.source,
                                 content=lyric)
        return self._lyric

    @lyric.setter
    def lyric(self, value):
        self._lyric = value

    @property
    def comments(self):
        comments_data = self._api.song_comments(self.identifier)
        self._comments = []
        if 'hotComments' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotComments']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['user']['userId'],
                                   content=comment_data['content'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    def similar_songs(self):
        songs = []
        songs_data = self._api.similar_songs(self.identifier)
        for song_data in songs_data:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return songs

    def similar_playlists(self):
        playlists = []
        playlists_data = self._api.similar_playlists(self.identifier)
        for playlist_data in playlists_data:
            playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
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


class NAlbumModel(AlbumModel, NBaseModel):
    _detail_fields = ('cover', 'songs', 'artists')

    @classmethod
    def get(cls, identifier):
        album_data = cls._api.album_detail(identifier)
        if album_data is None:
            return None
        album, _ = NeteaseAlbumSchema(strict=True).load(album_data)
        return album

    @property
    def desc(self):
        if self._desc is None:
            self._desc = self._api.album_desc(self.identifier)
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    @property
    def comments(self):
        comments_data = self._api.album_comments(self.identifier)
        self._comments = []
        if 'hotComments' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotComments']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['user']['userId'],
                                   content=comment_data['content'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value


class NArtistModel(ArtistModel, NBaseModel):
    _detail_fields = ('cover', 'songs', 'albums')

    @classmethod
    def get(cls, identifier):
        _artist_data, _ = cls._api.artist_detail(identifier)
        artist_data = _artist_data['artist']
        artist_data['songs'] = _artist_data['hotSongs'] or []
        artist_data['albums'], _ = cls._api.artist_albums(identifier)
        artist, _ = NeteaseArtistSchema(strict=True).load(artist_data)
        return artist

    @property
    def desc(self):
        if self._desc is None:
            self._desc = self._api.artist_desc(self.identifier)
        return self._desc

    @desc.setter
    def desc(self, value):
        self._desc = value

    # @property
    # def comments(self):
    #     self._comments = []
    #     return self._comments
    #
    # @comments.setter
    # def comments(self, value):
    #     self._comments = value

    def similar_artists(self):
        artists = []
        artists_data = self._api.similar_artists(self.identifier)
        for artist_data in artists_data:
            artist, _ = NeteaseArtistSchema(strict=True).load(artist_data)
            artists.append(artist)
        return artists


class NPlaylistModel(PlaylistModel, NBaseModel):
    # 默认url:'http://p4.music.126.net/tGHU62DTszbFQ37W9qPHcg==/2002210674180197.jpg'
    _detail_fields = ('cover', 'songs')

    class Meta:
        fields = ('uid',)

    @classmethod
    def get(cls, identifier):
        playlist_data = cls._api.playlist_detail(identifier)
        playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
        return playlist

    @property
    def comments(self):
        comments_data = self._api.playlist_comments(self.identifier)
        self._comments = []
        if 'hotComments' not in comments_data:
            return self._comments
        for comment_data in comments_data['hotComments']:
            comment = CommentModel(identifier=comment_data['commentId'],
                                   source=self.source,
                                   uid=comment_data['user']['userId'],
                                   content=comment_data['content'])
            self._comments.append(comment)
        return self._comments

    @comments.setter
    def comments(self, value):
        self._comments = value

    @classmethod
    def create(cls, user_id, name='default'):
        playlist_data = cls._api.new_playlist(user_id, name)
        playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
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
            song = NSongModel.get(song_id)
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


class NUserModel(UserModel, NBaseModel):
    _detail_fields = ('playlists', 'fav_songs', 'fav_albums', 'fav_artists', 'fav_playlists')

    @classmethod
    def get(cls, identifier):
        _user_data = cls._api.user_detail(identifier)
        user_data = {'id': identifier,
                     'name': _user_data['nickname'],
                     'cover': _user_data['avatarUrl'],
                     'cookies': cls._api.cookies}
        playlists, _ = cls._api.user_playlists(identifier)

        user_data['playlists'] = []
        user_data['fav_songs'] = []
        user_data['fav_playlists'] = []
        for pl in playlists:
            if pl['specialType'] == 5:
                user_data['fav_songs'] = cls._api.playlist_detail(pl['id'])['tracks']
            elif pl['userId'] == identifier:
                user_data['playlists'].append(pl)
            else:
                user_data['fav_playlists'].append(pl)

        user_data['fav_albums'], _info = cls._api.user_favorite_albums(limit=200)
        while _info['more']:
            _fav_albums, _info = cls._api.user_favorite_albums(_info['next'], 200)
            user_data['fav_albums'].extend(_fav_albums)

        user_data['fav_artists'], _info = cls._api.user_favorite_artists(limit=200)
        while _info['more']:
            _fav_artists, _info = cls._api.user_favorite_artists(_info['next'], 200)
            user_data['fav_artists'].extend(_fav_artists)

        user, _ = NeteaseUserSchema(strict=True).load(user_data)
        return user

    def fm_songs(self):
        songs_data = self._api.personal_fm()
        songs = []
        for song_data in songs_data:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return songs

    def recommend_songs(self):
        songs_data = self._api.recommend_songs()
        songs = []
        for song_data in songs_data:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return songs

    def recommend_playlists(self):
        playlists_data = self._api.recommend_playlists()
        playlists = []
        for playlist_data in playlists_data:
            playlist_data = self._api.playlist_detail(playlist_data['id'])
            playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
            playlists.append(playlist)
        return playlists


class NBillboardModel(BillboardModel, NBaseModel):
    _detail_fields = ('t', 'cover', 'songs')

    @classmethod
    def get(cls, identifier):
        songs_data = cls._api.top_songlist(identifier['id'])
        songs = []
        for song_data in songs_data:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return NBillboardModel(source=provider.identifier,
                               t=identifier['name'],
                               # cover=songs[0].album.cover,
                               songs=songs)

    @staticmethod
    def dicts():
        items = []
        for item in provider.api.return_toplists().values():
            items.append({'id': item[1],
                          'name': item[0]})
        return items


class NRecommendationModel(RecommendationModel, NBaseModel):
    _detail_fields = ('r', 'playlists')

    @classmethod
    def get(cls, identifier):
        playlists_data, _ = cls._api.top_playlists(identifier)
        playlists = []
        for playlist_data in playlists_data:
            playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
            playlists.append(playlist)
        return NRecommendationModel(source=provider.identifier,
                                    r=identifier,
                                    playlists=playlists)

    @staticmethod
    def dicts():
        items_data = provider.api.return_playlist_classes()
        items = []
        for item_data in items_data[0]:
            items.append({'classes': item_data,
                          'items': items_data[1][item_data]})
        return items


class NSearchModel(SearchModel, NBaseModel):
    pass


def search(keyword, **kwargs):
    songs_data, _ = provider.api.search(keyword)
    id_song_map = {}
    songs = []
    if songs_data:
        for song_data in songs_data:
            id_song_map[str(song_data['id'])] = song_data
            schema = NeteaseSongSchema(strict=True)
            song, _ = schema.load(song_data)
            songs.append(song)
    return NSearchModel(source=provider.identifier,
                        q=keyword,
                        songs=songs)


# import loop
from .schemas import (
    NeteaseSongSchema,
    NeteaseAlbumSchema,
    NeteaseArtistSchema,
    NeteasePlaylistSchema,
    NeteaseUserSchema,
)  # noqa
