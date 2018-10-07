# -*- coding: utf-8 -*-
import base64

from marshmallow import Schema, post_load, fields

from fuocore.models import (
    AlbumModel,
    ArtistModel,
    SongModel,
)
from fuocore.utils import elfhash

from marshmallow import Schema, fields, post_load


SOURCE = 'local'


class BaseSchema(Schema):
    identifier = fields.Field(required=True)
    source = fields.Str(required=True, missing=SOURCE)
    desc = fields.Str()


class ArtistSchema(BaseSchema):
    # TODO: 添加一个 alias 字段？
    name = fields.Str(required=True)
    cover = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('SongSchema'))

    @post_load
    def create_model(self, data):
        return ArtistModel(**data)


class AlbumSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()
    songs = fields.List(fields.Nested('SongSchema'))
    artists = fields.List(fields.Nested(ArtistSchema))

    @post_load
    def create_model(self, data):
        return AlbumModel(**data)


class SongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)  # mileseconds
    album = fields.Nested(AlbumSchema)
    artists = fields.List(fields.Nested(ArtistSchema))

    @post_load
    def create_model(self, data):
        return SongModel(**data)


class EasyMP3MetadataSongSchema(Schema):
    """EasyMP3 metadata"""
    url = fields.Str(required=True)
    title_list = fields.List(fields.Str(), load_from='title', required=True)
    duration = fields.Float(required=True)
    artist_name_list = fields.List(fields.Str(), load_from='artist')
    album_name_list = fields.List(fields.Str(), load_from='album')

    @post_load
    def create_song_model(self, data):
        title_list = data.get('title_list', [])
        title = title_list[0] if title_list else 'Unknown'
        artist_name_list = data.get('artist_name_list', [])
        album_name_list = data.get('album_name_list', [])
        identifier = str(elfhash(base64.b64encode(bytes(data['url'], 'utf-8'))))
        song_data = {
            'source': SOURCE,
            'identifier': identifier,
            'title': title,
            'duration': data['duration'],
            'url': data['url'],
            'artists': [{'name': name, 'identifier': name, 'source': SOURCE}
                        for name in artist_name_list]
        }
        if album_name_list:
            song_data['album'] = {'name': album_name_list[0],
                                  'identifier': album_name_list[0],
                                  'source': SOURCE}
        song, _ = SongSchema(strict=True).load(song_data)
        return song
