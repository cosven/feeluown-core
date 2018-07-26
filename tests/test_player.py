import os
import time
from unittest import TestCase, skipIf

from fuocore.player import MpvPlayer, Playlist


MP3_URL = os.path.join(os.path.dirname(__file__),
                       '../data/fixtures/ybwm-ts.mp3')


class FakeSongModel:  # pylint: disable=all
    pass


class TestPlayer(TestCase):
    def setUp(self):
        self.player = MpvPlayer()
        self.player.initialize()

    def tearDown(self):
        self.player.shutdown()

    @skipIf(os.environ.get('TEST_ENV', 'travis'), '')
    def test_play(self):
        self.player.play(MP3_URL)
        self.player.stop()

    @skipIf(os.environ.get('TEST_ENV', 'travis'), '')
    def test_duration(self):
        # This may failed?
        self.player.play(MP3_URL)
        time.sleep(0.1)
        self.assertIsNotNone(self.player.duration)

    @skipIf(os.environ.get('TEST_ENV', 'travis'), '')
    def test_seek(self):
        self.player.play(MP3_URL)
        time.sleep(0.1)
        self.player.position = 100


class TestPlaylist(TestCase):
    def setUp(self):
        self.s1 = FakeSongModel()
        self.s2 = FakeSongModel()
        self.playlist = Playlist()
        self.playlist.add(self.s1)
        self.playlist.add(self.s2)

    def tearDown(self):
        self.playlist.clear()

    def test_add(self):
        self.playlist.add(self.s1)
        self.assertEqual(len(self.playlist), 2)

    def test_remove_current_song(self):
        s3 = FakeSongModel()
        self.playlist.add(s3)
        self.playlist.current_song = self.s2
        self.playlist.remove(self.s2)
        self.assertEqual(self.playlist.current_song, s3)
        self.assertEqual(len(self.playlist), 2)

    def test_remove(self):
        self.playlist.remove(self.s1)
        self.assertEqual(len(self.playlist), 1)
