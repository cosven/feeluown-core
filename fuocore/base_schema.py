# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class ArtistSchema(Schema):
    name = fields.String()


class AlbumModel(Schema):
    name = fields.String()
    artists = fields.List(fields.Nested(ArtistSchema))
    img = fields.Url()
    desc = fields.String()


class SongSchema(Schema):
    title = fields.String()
    artists = fields.List(fields.Nested(ArtistSchema))
    album = fields.Nested(AlbumModel)
    url = fields.Url()
    length = fields.TimeDelta(precision='microseconds')
    source = fields.String()


class MvSchema(Schema):
    title = fields.String()
    song = fields.Nested(SongSchema)
    url = fields.Url()


class PlaylistSchema(Schema):
    name = fields.String()
    songs = fields.List(fields.Nested(SongSchema))
