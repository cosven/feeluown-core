# -*- coding: utf-8 -*-

import logging

from fuocore.provider import register, get_provider, providers
from fuocore.furi import parse_furi


logger = logging.getLogger(__name__)


class Source(object):

    def search(self, keyword):
        """search song by keyword"""
        songs = []
        for provider in providers:
            _songs = list(provider.search(keyword=keyword))
            logger.debug('在 provider({}) 中搜索到了 {} 首歌曲'
                         .format(provider.name, len(_songs)))
            songs.extend(_songs)
        logger.debug('共搜索到了 {} 首关于 {} 的歌曲'.format(len(songs), keyword))
        return songs

    def get_song(self, song_furi_str):
        """get song from identifier"""
        furi = parse_furi(song_furi_str)
        provider = get_provider(furi.provider)
        return provider.get_song(furi.identifier)
