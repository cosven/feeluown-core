# -*- coding: utf-8 -*-

import logging
from collections import defaultdict
from urllib.parse import urlparse

from .provider import get_provider, providers
from .furi import parse_furi


logger = logging.getLogger(__name__)


class Source(object):
    """
    XXX: unstable api
    """
    def __init__(self, prvs=None):
        self.providers = prvs or providers

    def register(self, provider):
        self.providers.add(provider)

    def search(self, keyword):
        """search song by keyword"""
        songs = []
        for provider in providers:
            _songs = list(provider.search(keyword=keyword))
            logger.debug('在 provider({}) 中搜索到了 {} 首歌曲'
                         .format(provider.name, len(_songs)))
            songs.extend(_songs)
        logger.debug('共搜索到了 {} 首关于 {} 的歌曲'.format(len(songs), keyword))
        return songs[:40]

    def get_song(self, furi_str):
        """get song from identifier"""
        result = urlparse(furi_str)
        provider = get_provider(result.netloc)
        identifier = result.path.split('/')[-1]
        return provider.get_song(identifier)

    def list_songs(self, furi_str_list):
        provider_songs_map = defaultdict(list)
        for furi_str in furi_str_list:
            furi = parse_furi(furi_str)
            provider_songs_map[furi.provider].append(furi.identifier)
        songs = []
        for provider_name, identifiers in provider_songs_map.items():
            provider = get_provider(provider_name)
            songs += provider.list_songs(identifiers)
        return songs
