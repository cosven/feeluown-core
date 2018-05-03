import logging

from marshmallow.exceptions import ValidationError

from fuocore.utils import log_exectime
from fuocore.core.provider import AbstractProvider
from fuocore.netease.api import api
from fuocore.netease.schemas import (
    NeteaseAlbumSchema,
    NeteaseArtistSchema,
    NeteasePlaylistSchema,
    NeteaseSongSchema,
    NeteaseUserSchema,
)

from fuocore.netease.models import (
    NAlbumModel,
    NArtistModel,
    NSongModel,
    NPlaylistModel,
)


logger = logging.getLogger(__name__)


class NeteaseProvider(AbstractProvider):
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
                    yield s
        return []

    def get_song(self, identifier):
        return NSongModel.get(identifier)

    def get_lyric(self, song_id):
        data = api.get_lyric_by_songid(song_id)
        lrc = data.get('lrc', {})
        lyric = lrc.get('lyric', '')
        return lyric

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
        return NAlbumModel.get(identifier)

    def get_artist(self, identifier):
        return NArtistModel.get(identifier)

    def get_playlist(self, identifier):
        playlist_data = api.playlist_detail(identifier)
        playlist, _ = NeteasePlaylistSchema(strict=True).load(playlist_data)
        return playlist
