# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, post_load

from fuocore.models import SongModel


class BaseSchema(Schema):
    identifier = fields.Field(required=True)
    source = fields.Str(required=True)
    desc = fields.Str()


class ArtistSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('SongSchema'))


class AlbumSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('SongSchema'))
    artists = fields.List(fields.Nested(ArtistSchema))


class SongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)
    album = fields.Nested(AlbumSchema)
    artists = fields.List(fields.Nested(ArtistSchema))

    @post_load
    def create_model(self, data):
        return SongModel(**data)

class LyricSchema(BaseSchema):
    content = fields.Str(required=True)
    trans_content = fields.Str()   # 翻译之后的歌词
