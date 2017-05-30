import os
from unittest import TestCase

import mock

from fuocore.consts import MUSIC_LIBRARY_PATH
from fuocore.provider import LocalProvider


class TestLocalProvider(TestCase):
    def setUp(self):
        self.local_pvd = LocalProvider(['data/test_music/'])

    def tearDown(self):
        pass

    def test__scan_dir(self):
        media_files = self.local_pvd.scan()
        self.assertEqual(
            set(media_files),
            set([
                'data/test_music/one_tree.mp3',
                'data/test_music/favorite/We Are Never Ever Getting Back '
                'Together - Taylor Swift.mp3',
            ])
        )

    def test_add_to_library(self):
        self.local_pvd.add_to_library('data/test_music/favorite/')
        self.assertIn('data/test_music/favorite/', self.local_pvd.library_paths)
        self.assertEqual(len(self.local_pvd.songs), 2)

    def test_search(self):
        """you should know that the metadata of *love_story.mp3* """

        songs = self.local_pvd.search(u'taylor')
        self.assertIn('swift', str(songs[0]).lower())

    def test_model_from_fpath(self):
        fpath = 'data/test_music/one_tree.mp3'
        song = self.local_pvd.model_from_fpath(fpath)
        self.assertEqual(song.name, 'unknown')
        self.assertEqual(song.source, 'local')
        self.assertEqual(song.brief_artists[0].source, 'local')
