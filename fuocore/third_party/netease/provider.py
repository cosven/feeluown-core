from fuocore.provider import AbstractProvider
from fuocore.models import BriefSongModel

from .api import api
from .schemas import BriefSongSchema


class NeteaseProvider(AbstractProvider):

    @property
    def name(self):
        return 'netease'

    def search(self, keywords='', **kwargs):
        songs = api.search(keywords)
        models = []
        brief_song_schema = BriefSongSchema()
        for song in songs:
            result = brief_song_schema.load(song)
            model = BriefSongModel.deserialize(result.data)
            models.append(model)
        return models
