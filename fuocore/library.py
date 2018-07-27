import logging

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
