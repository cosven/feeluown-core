# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, post_load

from fuocore.models import (
    AlbumModel,
    ArtistModel,
    PlaylistModel,
    SongModel,
    UserModel,
)


class BaseSchema(Schema):
    identifier = fields.Field(required=True)
    source = fields.Str(required=True)
    desc = fields.Str()


class ArtistSchema(BaseSchema):
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


class LyricSchema(BaseSchema):
    content = fields.Str(required=True)
    trans_content = fields.Str()   # 翻译之后的歌词


class CommentSchema(BaseSchema):
    user_id = fields.Str()
    content = fields.Str(required=True)


class SongSchema(BaseSchema):
    title = fields.Str(required=True)
    url = fields.Str(required=True)
    duration = fields.Float(required=True)  # mileseconds
    album = fields.Nested(AlbumSchema)
    artists = fields.List(fields.Nested(ArtistSchema))
    lyric = fields.Nested(LyricSchema)
    comments = fields.List(fields.Nested(CommentSchema))

    @post_load
    def create_model(self, data):
        return SongModel(**data)


class PlaylistSchema(BaseSchema):
    name = fields.Str(required=True)
    cover = fields.Url()
    desc = fields.Str()
    songs = fields.List(fields.Nested(SongSchema))

    @post_load
    def create_model(self, data):
        return PlaylistModel(**data)


class UserSchema(BaseSchema):
    name = fields.Str(required=True)
    playlists = fields.List(fields.Nested(PlaylistSchema))

    @post_load
    def create_model(self, data):
        return UserModel(**data)
