# -*- coding: utf-8 -*-
import base64

from marshmallow import Schema, post_load, fields
from marshmallow import Schema, fields, post_load

from fuocore.utils import elfhash


class BaseSchema(Schema):
    identifier = fields.Field(required=True)
    desc = fields.Str()


class ArtistSchema(BaseSchema):
    # TODO: 添加一个 alias 字段？
    name = fields.Str(required=True)
    cover = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('SongSchema'))
    albums = fields.List(fields.Nested('AlbumSchema'))

    @post_load
    def create_model(self, data):
        return LArtistModel(**data)


class AlbumSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()
    songs = fields.List(fields.Nested('SongSchema'))
    artists = fields.List(fields.Nested(ArtistSchema))

    @post_load
    def create_model(self, data):
        return LAlbumModel(**data)


class SongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)  # mileseconds
    album = fields.Nested(AlbumSchema)
    artists = fields.List(fields.Nested(ArtistSchema))

    @post_load
    def create_model(self, data):
        return LSongModel(**data)


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
        artists_name = ','.join(artist_name_list)
        album_name = album_name_list[0] if album_name_list else ''
        # NOTE: use {title}-{artists_name}-{album_name} as song identifier
        identifier_str = '{} - {} - {}'.format(title, artists_name, album_name)
        identifier = str(elfhash(base64.b64encode(bytes(identifier_str, 'utf-8'))))
        song_data = {
            'identifier': identifier,
            'title': title,
            'duration': data['duration'],
            'url': data['url']
        }
        if album_name_list:
            song_data['album'] = {'name': album_name_list[0],
                                  'identifier': album_name_list[0],
                                  'artists': [],
                                  'songs': []}

        if artist_name_list:
            artists = []
            for artist_name in artist_name_list:
                artist = {'identifier': elfhash(base64.b64encode(bytes(artist_name, 'utf-8'))),
                          'name': artist_name,
                          'albums': [],
                          'songs': []}
                artists.append(artist)
            song_data['artists'] = artists

        song, _ = SongSchema(strict=True).load(song_data)
        return song


from .provider import (
    LAlbumModel,
    LArtistModel,
    LSongModel,
)
