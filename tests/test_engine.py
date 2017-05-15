import copy
import os
from unittest import TestCase

import mock

from fuocore.engine import Player, Playlist
from fuocore.models import SongModel
from fuocore.dispatch import Signal

MP3_URL = os.path.join(os.path.dirname(__file__), 'fixtures', 'ybwm-ts.mp3')


fake_song = SongModel(**{
    'id': 1,
    'name': 'hello world',
    'url': MP3_URL,
    'brief_album': {
        'name': 'hybrid'
    },
    'brief_artists': [
        {
            'name': 'Linkin Park'
        }
    ]
})
fake_song_1 = copy.deepcopy(fake_song)
fake_song_1.id = 2


class TestPlaylist(TestCase):
    def setUp(self):
        self.playlist = Playlist([fake_song, fake_song_1])

    def test_set_current_song(self):
        self.playlist.current_song = fake_song
        self.assertEqual(self.playlist.current_song, fake_song)

    def test_next_when_no_current_song(self):
        self.playlist.next()
        self.assertEqual(self.playlist.current_song, fake_song)

    def test_next_when_in_loop_mode(self):
        self.playlist.current_song = fake_song
        self.playlist.next()
        self.assertEqual(self.playlist.current_song, fake_song_1)

    def test_previous_when_no_current_song_and_no_last_song(self):
        self.playlist.previous()
        self.assertEqual(self.playlist.current_song, fake_song)

    @mock.patch.object(Signal, 'emit')
    def test_set_current_song_should_emit_signal(self, mock_emit):
        self.playlist.previous()
        self.assertTrue(mock_emit.called)


class TestPlayer(TestCase):
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

    def test_play_song(self):
        self.player.play_song(fake_song)
        self.assertTrue(self.player.current_song == fake_song)
        # time.sleep(1)
        # self.assertTrue(self.player.state == State.playing)

    @mock.patch.object(Player, 'play_song')
    def test_play_songs(self, mock_play_song):
        self.player.play_songs([fake_song, fake_song])
        self.assertTrue(mock_play_song.called)

    def test_add_song(self):
        self.player.add_song(fake_song)
        self.assertTrue(len(self.player.songs), 1)

    def test_get_next_song(self):
        self.player.play_songs([fake_song, fake_song])
        self.assertTrue(self.player.get_next_song() == fake_song)
