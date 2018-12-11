# -*- coding: utf-8 -*-
import re
import base64

from marshmallow import Schema, fields, post_load

from fuocore.utils import elfhash


class BaseSchema(Schema):
    identifier = fields.Field(required=True, missing=None)
    desc = fields.Str()


class LocalArtistSchema(BaseSchema):
    # TODO: 添加一个 alias 字段？
    name = fields.Str(required=True)
    cover = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('LocalSongSchema'), missing=None)
    albums = fields.List(fields.Nested('LocalAlbumSchema'), missing=None)

    @post_load
    def create_model(self, data):
        if data['identifier'] is None:
            data['identifier'] = str(elfhash(base64.b64encode(bytes(data['name'], 'utf-8'))))
        return LArtistModel(**data)


class LocalAlbumSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()
    songs = fields.List(fields.Nested('LocalSongSchema'), missing=None)
    artists = fields.List(fields.Nested(LocalArtistSchema), missing=None)

    artists_name = fields.Str()

    @post_load
    def create_model(self, data):
        if data['identifier'] is None:
            identifier_str = '{} - {}'.format(data['name'], data['artists_name'])
            data['identifier'] = str(elfhash(base64.b64encode(bytes(identifier_str, 'utf-8'))))
        album = LAlbumModel(**data)
        if album.artists is None and data['artists_name']:
            album_artist, _ = LocalArtistSchema(strict=True).load({'name': data['artists_name']})
            album.artists = [album_artist]
        return album


class LocalSongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)  # mileseconds
    album = fields.Nested(LocalAlbumSchema, missing=None)
    artists = fields.List(fields.Nested(LocalArtistSchema), missing=None)

    @post_load
    def create_model(self, data):
        return LSongModel(**data)

class EasyMP3MetadataSongSchema(Schema):
    """EasyMP3 metadata"""
    url = fields.Str(required=True)
    duration = fields.Float(required=True)
    title = fields.Str(required=True, missing='Unknown')
    artists_name = fields.Str(required=True, load_from='artist', missing='')
    album_name = fields.Str(required=True, load_from='album', missing='')
    album_artist_name = fields.Str(required=True, load_from='albumartist', missing='')
    track = fields.Str(load_from='tracknumber')
    disc = fields.Str(load_from='discnumber')
    date = fields.Str()
    genre = fields.Str()

    @post_load
    def create_model(self, data):
        # NOTE: use {title}-{artists_name}-{album_name} as song identifier
        identifier_str = '{} - {} - {} - {}'.format(data['title'], data['artists_name'], data['album_name'],
                                                    data['duration'])
        data['identifier'] = str(elfhash(base64.b64encode(bytes(identifier_str, 'utf-8'))))
        song, _ = LocalSongSchema(strict=True).load(data)

        if song.album is None and data['album_name']:
            album_data = {'name': data['album_name'],
                          'artists_name': data['album_artist_name']}
            song.album, _ = LocalAlbumSchema(strict=True).load(album_data)

        if song.artists is None and data['artists_name']:
            song.artists = []
            artist_names = [artist.strip() for artist in re.split(r'[,&]', data['artists_name'])]
            for artist_name in artist_names:
                artist_data = {'name': artist_name}
                artist, _ = LocalArtistSchema(strict=True).load(artist_data)
                song.artists.append(artist)

        song.genre = data.get('genre', None)
        if song.album is not None:
            song.disc = data.get('disc', '1/1')
            song.track = data.get('track', '1/1')
            song.date = data.get('date', None)
        return song


from .models import (
    LAlbumModel,
    LArtistModel,
    LSongModel,
)
