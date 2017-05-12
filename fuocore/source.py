# -*- coding: utf-8 -*-

from .provider import register


class Source(object):
    _providers = set()

    def add_provider(self, provider):
        register(provider)
        self._providers.add(provider)

    def search(self, name=''):
        songs = []
        for provider in self._providers:
            songs.extend(provider.search(name=name))
        return songs
