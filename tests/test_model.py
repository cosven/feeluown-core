from unittest import TestCase

from fuocore.models import Model


class FakeProvider(object):
    name = 'fake'

    def set_model_cls(self, *args, **kwags):
        pass


provider = FakeProvider()


class TestModel(TestCase):

    def test_meta_class(self):

        class SongModel(Model):
            class Meta:
                provider = provider

        song = SongModel()
        self.assertEqual(song._meta.provider.name, 'fake')

    def test_meta_class_inherit(self):
        class SongModel(Model):
            class Meta:
                model_type = 1  # song model

        class LastSongModel(SongModel):
            pass

        song = LastSongModel()
        self.assertEqual(song._meta.model_type, 1)

    def test_meta_class_inherit_with_override(self):
        class SongModel(Model):
            class Meta:
                model_type = 1  # song model

        class LastSongModel(SongModel):
            class Meta:
                provider = provider

        song = LastSongModel()
        self.assertEqual(song._meta.model_type, 1)
        self.assertEqual(song._meta.provider.name, 'fake')
