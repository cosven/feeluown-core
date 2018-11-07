import os
import time
from unittest import TestCase, skipIf

from fuocore.player import MpvPlayer, Playlist, PlaybackMode, State


MP3_URL = os.path.join(os.path.dirname(__file__),
                       '../data/fixtures/ybwm-ts.mp3')


class FakeSongModel:  # pylint: disable=all
    pass


class FakeValidSongModel:
    url = MP3_URL


class TestPlayer(TestCase):

    def setUp(self):
        self.player = MpvPlayer()
        self.player.initialize()

    def tearDown(self):
        self.player.shutdown()

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_play(self):
        self.player.play(MP3_URL)
        self.player.stop()

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_duration(self):
        # This may failed?
        self.player.play(MP3_URL)
        time.sleep(0.1)
        self.assertIsNotNone(self.player.duration)

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_seek(self):
        self.player.play(MP3_URL)
        time.sleep(0.1)
        self.player.position = 100

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_replay(self):
        song = FakeValidSongModel()
        self.player.play_song(song)
        time.sleep(0.1)
        self.player.position = 100
        self.player.replay()
        time.sleep(0.1)
        self.assertTrue(self.player.position < 10)

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_play_pause_toggle_resume_stop(self):
        self.player.play(MP3_URL)
        time.sleep(0.1)
        self.player.toggle()
        self.assertEqual(self.player.state, State.paused)
        self.player.resume()
        self.assertEqual(self.player.state, State.playing)
        self.player.pause()
        self.assertEqual(self.player.state, State.paused)
        self.player.stop()
        self.assertEqual(self.player.state, State.stopped)

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_set_volume(self):
        self.player.volume = 30
        self.assertEqual(self.player.volume, 30)


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

    def test_remove_2(self):
        """播放器正在播放，移除一首歌"""
        self.playlist.current_song = self.s2
        self.playlist.remove(self.s1)
        self.assertEqual(self.playlist.current_song, self.s2)
        self.assertEqual(len(self.playlist), 1)

    def test_remove_3(self):
        """移除一首不存在的歌"""
        self.playlist.remove(FakeSongModel())
        self.assertEqual(len(self.playlist), 2)

    def test_remove_3(self):
        """移除一首被标记为无效的歌曲"""
        self.playlist.mark_as_bad(self.s2)
        self.assertEqual(len(self.playlist._bad_songs), 1)
        self.playlist.remove(self.s2)
        self.assertEqual(len(self.playlist), 1)
        self.assertEqual(len(self.playlist._bad_songs), 0)

    def test_getitem(self):
        self.assertEqual(self.playlist[1], self.s2)

    def test_mark_as_bad(self):
        self.assertEqual(self.playlist.next_song, self.s1)
        self.playlist.mark_as_bad(self.s1)
        self.assertEqual(self.playlist.next_song, self.s2)

    def test_list(self):
        self.assertIn(self.s1, self.playlist.list())

    def test_set_current_song(self):
        """将一首不存在于播放列表的歌曲设置为当前播放歌曲"""
        s3 = FakeSongModel()
        self.playlist.current_song = s3
        self.assertIn(s3, self.playlist)

    def test_next_song(self):
        self.playlist.playback_mode = PlaybackMode.sequential
        self.playlist.current_song = self.s2
        self.assertIsNone(self.playlist.next_song)
        self.playlist.playback_mode = PlaybackMode.random
        self.playlist.next_song  # assert no exception

    def test_previous_song(self):
        self.assertEqual(self.playlist.previous_song, self.s2)
        self.playlist.current_song = self.s2
        self.assertEqual(self.playlist.previous_song, self.s1)


class TestPlayerAndPlaylist(TestCase):

    def setUp(self):
        self.player = MpvPlayer()
        self.playlist = self.player.playlist
        self.player.initialize()

    def tearDown(self):
        self.playlist.clear()
        self.player.shutdown()

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_change_song(self):
        s1 = FakeValidSongModel()
        s2 = FakeValidSongModel()

        playlist = self.player.playlist
        playlist.add(s1)
        playlist.add(s2)

        self.player.play_song(s1)
        self.player.play_next()
        self.assertTrue(playlist.current_song, s2)

        self.player.play_previous()
        self.assertTrue(playlist.current_song, s1)

    @skipIf(os.environ.get('TEST_ENV') == 'travis', '')
    def test_remove_current_song_2(self):
        """当播放列表只有一首歌时，移除它"""
        s1 = FakeValidSongModel()
        self.playlist.current_song = s1
        time.sleep(0.1)  # 让 Mpv 真正的开始播放
        self.assertTrue(self.player.state, State.playing)
        self.playlist.remove(s1)
        self.assertEqual(len(self.playlist), 0)
        self.assertEqual(self.player.state, State.stopped)
