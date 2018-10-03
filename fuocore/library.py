"""
fuocore.library
---------------
"""

import logging

logger = logging.getLogger(__name__)


class Library(object):
    """library manages a set of providers

    library is the entry point for music resources
    """
    def __init__(self):
        self._providers = set()

    def register(self, provider):
        """add a provider to library"""
        self._providers.add(provider)

    def deregister(self, provider):
        """remove a provider to library"""
        self._providers.remove(provider)

    def get(self, identifier):
        """get provider by id"""
        for provider in self._providers:
            if provider.identifier == identifier:
                return provider
        return None

    def list(self):
        """list all providers"""
        return list(self._providers)

    def search(self, keyword, source_in=None, **kwargs):
        """search song/artist/album by keyword

        TODO: search album or artist
        TODO: return a generator?
        """
        for provider in self._providers:
            if source_in is not None:
                if provider.identifier not in source_in:
                    continue
            if not provider.search:
                continue

            try:
                result = provider.search(keyword=keyword)
            except Exception as e:
                logger.exception(str(e))
                logger.error('Search %s in %s failed.' % (keyword, provider))
            else:
                yield result
