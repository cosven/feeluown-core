import os
from unittest import TestCase

from fuocore.player import Player

MP3_URL = os.path.join(os.path.dirname(__file__), 'fixtures', 'ybwm-ts.mp3')


class PlayerTest(TestCase):
    def setUp(self):
        self.player = Player()

    def test_handler(self):
        self.assertIsNotNone(self.player.handler)

    def tearDown(self):
        self.player.shutdown()

    def test_play(self):
        self.player.play()

    def test_pause(self):
        self.player._play(MP3_URL)
        self.player.pause()

    def test_toggle(self):
        self.player.toggle()

    def test_position(self):
        self.player.position
