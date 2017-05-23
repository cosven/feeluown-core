# -*- coding: utf-8 -*-

from .provider import register


class Source(object):

    def __init__(self):
        self._providers = set()

    def add_provider(self, provider):
        register(provider)
        self._providers.add(provider)

    def search(self, keyword):
        """search song by keyword

        :returns: list of :class:`fuocore.models.BriefSongModel`
        """
        songs = []
        for provider in self._providers:
            songs.extend(provider.search(keyword=keyword))
        return songs

    def get_song(self, identifier):
        """get song from identifier"""
