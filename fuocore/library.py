import logging
from urllib.parse import urlparse
from collections import defaultdict

logger = logging.getLogger(__name__)


class Library(object):
    def __init__(self):
        self._providers = set()

    def register(self, provider):
        self._providers.add(provider)

    def deregister(self, provider):
        self._providers.remove(provider)

    def get(self, identifier):
        for provider in self._providers:
            if provider.identifier == identifier:
                return provider
        return None

    def list(self):
        return list(self._providers)

    def search(self, keyword):
        songs = []
        for provider in self._providers:
            if not provider.search:
                continue
            result = provider.search(keyword=keyword)
            _songs = list(result.songs[:20])
            logger.info('在 provider() 中搜索到了 {} 首歌曲'
                        .format(provider.name, len(_songs)))
            songs.extend(_songs)
        logger.debug('共搜索到了 {} 首关于 {} 的歌曲'
                     .format(len(songs), keyword))
        return songs

    def get_song(self, furi_str):
        """get song from identifier"""
        result = urlparse(furi_str)
        provider = self.get(result.netloc)
        identifier = result.path.split('/')[-1]
        return provider.Song.get(identifier)

    def list_songs(self, furi_str_list):
        provider_songs_map = defaultdict(list)
        for furi_str in furi_str_list:
            result = urlparse(furi_str)
            provider_id = result.netloc
            identifier = result.path.split('/')[-1]
            provider_songs_map[provider_id].append(identifier)
        songs = []
        for provider_id, song_ids in provider_songs_map.items():
            provider = self.get(provider_id)
            songs += provider.Song.list(song_ids)
        return songs
