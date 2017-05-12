from unittest import TestCase

from fuocore.models import BriefSongModel
from fuocore.third_party.netease import NeteaseProvider


class TestProvider(TestCase):
    def test_search_usage(self):
        ne_provider = NeteaseProvider()
        songs = ne_provider.search(u'hello world')
        self.assertTrue(isinstance(songs[0], BriefSongModel))
