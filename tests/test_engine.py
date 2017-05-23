import copy
import os
from unittest import TestCase

import mock

from fuocore.engine import Playlist
from fuocore.models import SongModel
from fuocore.dispatch import Signal

MP3_URL = os.path.join(os.path.dirname(__file__), 'fixtures', 'ybwm-ts.mp3')


data = {
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
}
fake_song = SongModel(**data)


class TestPlaylist(TestCase):
    def setUp(self):
        self.fake_song = SongModel(**data)
        data2 = copy.deepcopy(data)
        data2['id'] = 2
        self.fake_song_other = SongModel(**data2)
        self.playlist = Playlist([self.fake_song, self.fake_song_other])

    def test_set_current_song(self):
        self.playlist.current_song = self.fake_song
        self.assertEqual(self.playlist._current_index, 0)
        self.assertEqual(self.playlist.current_song, self.fake_song)

    def test_next_when_no_current_song(self):
        self.playlist.next()
        self.assertEqual(self.playlist.current_song, self.fake_song)

    def test_next_when_in_loop_mode(self):
        self.playlist.current_song = self.fake_song
        self.playlist.next()
        self.assertEqual(self.playlist.current_song, self.fake_song_other)

    def test_previous_when_no_current_song_and_no_last_song(self):
        self.playlist.previous()
        self.assertEqual(self.playlist.current_song, self.fake_song)

    @mock.patch.object(Signal, 'emit')
    def test_set_current_song_should_emit_signal(self, mock_emit):
        self.playlist.previous()
        self.assertTrue(mock_emit.called)

    def test_add_usage(self):
        song = SongModel(**data)
        self.playlist.add(song)
        self.assertEquals(len(self.playlist), 3)

    def test_getitem_overload(self):
        self.assertEqual(self.playlist[0], self.fake_song)
