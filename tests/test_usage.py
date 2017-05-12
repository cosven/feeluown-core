from unittest import TestCase

from fuocore import Source
from fuocore.third_party.netease import NeteaseProvider
from fuocore.models import BriefSongModel


class TestUsages(TestCase):

    def test_source_search(self):
        source = Source()
        neteae_provider = NeteaseProvider()
        source.add_provider(neteae_provider)
        songs = source.search(u'xxx')
        song = songs[0]
        self.assertTrue(isinstance(song, BriefSongModel))
