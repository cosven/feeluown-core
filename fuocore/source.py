# -*- coding: utf-8 -*-

from fuocore.provider import register, get_provider
from fuocore.furi import parse_furi


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

    def get_song(self, song_furi_str):
        """get song from identifier"""
        furi = parse_furi(song_furi_str)
        provider = get_provider(furi.provider)
        return provider.get_song(furi.identifier)
