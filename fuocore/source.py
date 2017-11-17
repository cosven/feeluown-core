# -*- coding: utf-8 -*-

from fuocore.provider import register, get_provider
from fuocore.utils import parse_indentifier

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
        result = parse_indentifier(identifier)
        provider_name = result.provider
        song_identifier = result.identifier
        provider = get_provider(provider_name)
        return provider.get_song(song_identifier)
