from fuocore.provider import AbstractProvider

from .api import api
from .schemas import BriefSongSchema, SongSchema, MediaSchema
from .models import NBriefSongModel, NSongModel, NMediaModel


class NeteaseProvider(AbstractProvider):

    @property
    def name(self):
        return 'netease'

    def search(self, keyword, **kwargs):
        songs = api.search(keyword)
        models = []
        brief_song_schema = BriefSongSchema()
        for song in songs:
            result = brief_song_schema.load(song)
            data = result.data
            data['source'] = self.name
            model = NBriefSongModel.deserialize(data)
            models.append(model)
        return models

    def get_song(self, id):
        medias = api.weapi_songs_url([id])
        media = medias[0]
        media_schema = MediaSchema()
        result = media_schema.load(media)
        media = NMediaModel.deserialize(result.data)

        song = api.song_detail(id)
        song_schema = SongSchema()
        result = song_schema.load(song)
        data = result.data
        data['url'] = media.url
        return NSongModel.deserialize(data)
