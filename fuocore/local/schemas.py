# -*- coding: utf-8 -*-
import re
import base64

from marshmallow import Schema, fields, post_load

from fuocore.utils import elfhash


class BaseSchema(Schema):
    identifier = fields.Field(required=True)
    desc = fields.Str()


class ArtistSchema(BaseSchema):
    # TODO: 添加一个 alias 字段？
    name = fields.Str(required=True)
    cover = fields.Str()  # NOTE: 可能需要单独一个 Schema
    songs = fields.List(fields.Nested('SongSchema'), missing=None)
    albums = fields.List(fields.Nested('AlbumSchema'), missing=None)

    @post_load
    def create_model(self, data):
        return LArtistModel(**data)


class AlbumSchema(BaseSchema):
    name = fields.Str(required=True)
    img = fields.Str()
    songs = fields.List(fields.Nested('SongSchema'), missing=None)
    artists = fields.List(fields.Nested(ArtistSchema), missing=[])

    @post_load
    def create_model(self, data):
        return LAlbumModel(**data)


class SongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)  # mileseconds
    album = fields.Nested(AlbumSchema, missing=None)
    artists = fields.List(fields.Nested(ArtistSchema), missing=[])

    @post_load
    def create_model(self, data):
        return LSongModel(**data)


class EasyMP3MetadataSongSchema(Schema):
    """EasyMP3 metadata"""
    url = fields.Str(required=True)
    title_list = fields.List(fields.Str(), load_from='title', required=True)
    duration = fields.Float(required=True)
    artist_list = fields.List(fields.Str(), load_from='artist')
    genre_list = fields.List(fields.Str(), load_from='genre')
    album_list = fields.List(fields.Str(), load_from='album')
    album_artist_list = fields.List(fields.Str(), load_from='albumartist')

    @post_load
    def create_song_model(self, data):
        # FIXME: 逻辑太多，请重构我，重构之前这里不应该添加新功能
        title = data['title_list'][0] if data.get('title_list') else 'Unknown'
        artists_name = data['artist_list'][0] if data.get('artist_list') else ''
        album_name = data['album_list'][0] if data.get('album_list') else ''
        # NOTE: use {title}-{artists_name}-{album_name} as song identifier
        song_identifier_str = '{} - {} - {}'.format(title, artists_name, album_name)
        song_identifier = str(elfhash(base64.b64encode(bytes(song_identifier_str, 'utf-8'))))
        song_data = {
            'identifier': song_identifier,
            'title': title,
            'duration': data['duration'],
            'url': data['url']
        }

        # album.songs需要统计之后统计
        if album_name:
            album_artist_name = data['album_artist_list'][0] if data.get('album_artist_list') else ''
            album_identifier_str = '{} - {}'.format(album_name, album_artist_name)
            album_identifier = str(elfhash(base64.b64encode(bytes(album_identifier_str, 'utf-8'))))
            song_data['album'] = {'identifier': album_identifier,
                                  'name': album_name}
            if album_artist_name:
                album_artist_identifier = str(elfhash(base64.b64encode(bytes(album_artist_name, 'utf-8'))))
                song_data['album']['artists'] = [{'identifier': album_artist_identifier,
                                                  'name': album_artist_name}]

        # artist.songs和artist.albums需要之后统计
        if artists_name:
            song_data['artists'] = []
            # Lin-Manuel Miranda, Leslie Odom Jr., Anthony Ramos, Daveed Diggs & Okieriete Onaodowan
            # 将其分解为'Lin-Manuel Miranda','Leslie Odom Jr.','Anthony Ramos','Daveed Diggs','Okieriete Onaodowan'
            artist_names = [artist.strip() for artist in re.split(r'[,&]', artists_name)]
            # TO DO: 特殊情况'陳樂基 & Killersoap殺手鐧'/'Macklemore & Ryan Lewis'/'Leslie Odom, Jr.'时不应该拆分
            for artist_name in artist_names:
                artist_identifier = str(elfhash(base64.b64encode(bytes(artist_name, 'utf-8'))))
                song_data['artists'].append({'identifier': artist_identifier,
                                             'name': artist_name})

        song, _ = SongSchema(strict=True).load(song_data)
        return song


from .models import (
    LAlbumModel,
    LArtistModel,
    LSongModel,
)
