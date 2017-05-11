# -*- coding: utf-8 -*-

from marshmallow import Schema, fields


class BriefArtistSchema(Schema):
    name = fields.String()


class BriefAlbumSchema(Schema):
    name = fields.String()


class BriefSongSchema(Schema):
    name = fields.String()
    duration = fields.Integer()
    brief_album = fields.Nested(BriefAlbumSchema, load_from='album')
    brief_artists = fields.List(fields.Nested(BriefArtistSchema), load_from='artists')
