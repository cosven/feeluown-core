import logging

from marshmallow.exceptions import ValidationError

from fuocore.decorators import log_exectime
from fuocore.provider import AbstractProvider
from fuocore.netease.api import api
from fuocore.netease.schemas import (
    NeteaseAlbumSchema,
    NeteaseArtistSchema,
    NeteasePlaylistSchema,
    NeteaseSongSchema,
    NeteaseUserSchema,
)


logger = logging.getLogger(__name__)


class NeteaseProvider(AbstractProvider):
    song_caches = {}  # TODO: 使用 LRU 策略？

    @property
    def name(self):
        return 'netease'

    def search(self, keyword, **kwargs):
        songs = api.search(keyword)
        id_song_map = {}
        if songs:
            for song in songs:
                id_song_map[str(song['id'])] = song
                schema = NeteaseSongSchema(strict=True)
                try:
                    s, _ = schema.load(song)
                except ValidationError:
                    logger.exception('反序列化出现异常')
                else:
                    self.song_caches[str(s.identifier)] = s
                    yield s
        return []

    def get_song(self, identifier):
        if identifier in self.song_caches:
            return self.song_caches[identifier]
        data = api.song_detail(int(identifier))
        song, _ = NeteaseSongSchema(strict=True).load(data)
        return song

    def list_songs(self, identifier_list):
        song_data_list = api.songs_detail(identifier_list)
        songs = []
        for song_data in song_data_list:
            song, _ = NeteaseSongSchema(strict=True).load(song_data)
            songs.append(song)
        return songs

    @log_exectime
    def get_user(self, identifier):
        user = {'id': identifier}
        user_brief = api.user_brief(identifier)
        user.update(user_brief)
        playlists = api.user_playlists(identifier)
        user['playlists'] = playlists
        user, _ = NeteaseUserSchema(strict=True).load(user)
        return user

    def get_album(self, identifier):
        album_data = api.album_infos(identifier)
        if album_data is None:
            return None
        songs = album_data['songs']
        songs_urls = api.weapi_songs_url([song['id'] for song in songs])
        for index, _ in enumerate(songs):
            songs[index]['url'] = songs_urls[index]['url']
        album_data['songs'] = songs
        album, _ = NeteaseAlbumSchema(strict=True).load(album_data)
        return album

    def get_artist(self, identifier):
        artist_data = api.artist_infos(identifier)
        songs = artist_data['hotSongs']
        songs_urls = api.weapi_songs_url([song['id'] for song in songs])
        for index, _ in enumerate(songs):
            songs[index]['url'] = songs_urls[index]['url']
        artist = artist_data['artist']
        artist['songs'] = songs
        artist, _ = NeteaseArtistSchema(strict=True).load(artist)
        return artist

    def get_playlist(self, identifier):
        playlist_data = api.playlist_detail(identifier)
        playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
        return playlist
