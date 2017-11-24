from marshmallow import Schema, post_load, fields

from fuocore.schemas import SongSchema
from fuocore.netease.models import NSongModel

SOURCE = 'netease'


class BriefAlbumSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    name = fields.Str(required=True)


class BriefArtistSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    name = fields.Str(required=True)


class NeteaseSongSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    title = fields.Str(required=True, load_from='name')
    duration = fields.Float(required=True)
    url = fields.Str(required=True)
    album = fields.Nested(BriefAlbumSchema, required=True)
    artists = fields.List(fields.Nested(BriefArtistSchema), required=True)

    @post_load
    def create_model(self, data):
        # FIXME: 改进这个代码，写的太糙了
        album = data['album']
        album['source'] = SOURCE
        artists = data['artists']
        for artist in artists:
            artist['source'] = SOURCE
        data['source'] = SOURCE
        data['album'] = album
        data['artists'] = artists
        song, _ = SongSchema(strict=True).load(data)
        return NSongModel(song)
