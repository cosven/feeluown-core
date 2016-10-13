import os
import time
from unittest import TestCase, mock

from fuocore.player import Player, State
from fuocore.base_model import SongModel

MP3_URL = os.path.join(os.path.dirname(__file__), 'fixtures', 'ybwm-ts.mp3') 


class FakeSongModel(SongModel):
    def __init__(self):
        pass

    @property
    def mid(self):
        return '00000000'

    @property
    def title(self):
        return 'fake-title'

    @property
    def url(self):
        return MP3_URL


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

    def test_play_song(self):
        song = FakeSongModel()
        self.player.play_song(song)
        self.assertTrue(self.player.current_song == song)
        # time.sleep(1)
        # self.assertTrue(self.player.state == State.playing)

    @mock.patch.object(Player, 'play_song')
    def test_play_songs(self, mock_play_song):
        song1 = FakeSongModel()
        song2 = FakeSongModel()
        self.player.play_songs([song1, song2])
        self.assertTrue(mock_play_song.called)

    def test_toggle(self):
        self.player.toggle()

    def test_position(self):
        self.player.position

    def test_add_song(self):
        song = FakeSongModel()
        self.player.add_song(song)
        self.assertTrue(len(self.player.songs), 1)

    def test_get_next_song(self):
        song1 = FakeSongModel()
        song2 = FakeSongModel()
        self.player.play_songs([song1, song2])
        self.assertTrue(self.player.get_next_song() == song2)

    def test_get_previous_song(self):
        pass
