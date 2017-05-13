from unittest import TestCase

from fuocore.models import BriefSongModel
from fuocore.third_party.netease import NeteaseProvider


class TestProvider(TestCase):

    def setUp(self):
        self.ne_provider = NeteaseProvider()

    def test_search_usage(self):
        songs = self.ne_provider.search(u'hello world')
        self.assertTrue(isinstance(songs[0], BriefSongModel))

    def test_get_song_usage(self):
        song = self.ne_provider.get_song(1)
        self.assertEqual(
            song.url,
            'http://m7.music.126.net/20170513125850/'
            '7c8cd88daa06eb5272c395a1977ae3b7/ymusic/'
            '6e01/a4d4/bbef/2dda07904eb54d44abb278165e1c6ead.mp3')
