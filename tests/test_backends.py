import os
from unittest import TestCase

from fuocore.backends import MpvPlayer
from fuocore.engine import State


MP3_URL = os.path.join(os.path.dirname(__file__), 'fixtures', 'ybwm-ts.mp3')


class TestPlayer(TestCase):
    def setUp(self):
        self.player = MpvPlayer()

    def tearDown(self):
        self.player.quit()

    def test_play(self):
        self.player.play(MP3_URL)
        self.assertEqual(self.player.state, State.playing)

    def test_pause(self):
        self.player.pause()
        self.assertEqual(self.player.state, State.paused)

    def test_toggle(self):
        self.player.toggle()
