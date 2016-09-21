from unittest import TestCase

from fuocore.player import Player


class PlayerTest(TestCase):
    def setUp(self):
        self.player = Player()

    def test_handler(self):
        self.assertIsNotNone(self.player.handler)

    def tearDown(self):
        self.player.destroy()

    def test_play(self):
        self.player.play()

    def test_pause(self):
        self.player.pause()

    def test_play_song(self):
        self.player.play_song('...')

    def test_next(self):
        self.player.next()

    def test_last(self):
        self.player.last()

    def test_toggle(self):
        self.player.toggle()

    def test_position(self):
        self.player.position
