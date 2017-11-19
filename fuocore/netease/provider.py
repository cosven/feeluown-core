import logging

from marshmallow.exceptions import ValidationError

from fuocore.provider import AbstractProvider
from fuocore.netease.api import api
from fuocore.netease.schemas import NeteaseSongSchema


logger = logging.getLogger(__name__)


class NeteaseProvider(AbstractProvider):
    song_caches = {}  # TODO: 使用 LRU 策略？

    @property
    def name(self):
        return 'netease'

    def search(self, keyword, **kwargs):
        songs = api.search(keyword)
        if songs:
            songs_urls = api.weapi_songs_url([song['id'] for song in songs])
            for song, song_url in zip(songs, songs_urls):
                song['url'] = song_url['url']
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
        urls = api.weapi_songs_url([int(identifier)])
        url = urls[0]['url']
        data['url'] = url
        song, _ = NeteaseSongSchema(strict=True).load(data)
        return song

    def get_album(self, identifier):
        pass

    def get_artist(self, identifier):
        pass
