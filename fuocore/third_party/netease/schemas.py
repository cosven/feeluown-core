# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class BriefArtistSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class BriefAlbumSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class BriefSongSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    duration = fields.Integer()
    brief_album = fields.Nested(BriefAlbumSchema, load_from='album')
    brief_artists = fields.List(fields.Nested(BriefArtistSchema), load_from='artists')


class SongSchema(BriefSongSchema):
    url = fields.Url(load_from='mp3Url')


class MediaSchema(Schema):
    id = fields.Integer()
    url = fields.Url()
    bitrate = fields.Integer(load_from='br')
