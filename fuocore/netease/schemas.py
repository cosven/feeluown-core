from marshmallow import Schema as _Schema, post_load, fields, pre_load

from fuocore.schemas import (
    AlbumSchema,
    ArtistSchema,
    PlaylistSchema,
    SongSchema,
    UserSchema,
)
from fuocore.models import UserModel


SOURCE = 'netease'


class Schema(_Schema):
    source = fields.Str(missing=SOURCE)


class NeteaseSongSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    title = fields.Str(required=True, load_from='name')
    duration = fields.Float(required=True)
    url = fields.Str(allow_none=True)
    album = fields.Nested('NeteaseAlbumSchema')
    artists = fields.List(fields.Nested('NeteaseArtistSchema'))

    @post_load
    def create_model(self, data):
        return NSongModel(**data)


class NeteaseAlbumSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    cover = fields.Str(load_from='picUrl', allow_none=True)
    songs = fields.List(fields.Nested('NeteaseSongSchema'))
    artists = fields.List(fields.Nested('NeteaseArtistSchema'))

    @post_load
    def create_model(self, data):
        return NAlbumModel(**data)


class NeteaseArtistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str()
    cover = fields.Str(load_from='picUrl', allow_none=True)
    songs = fields.List(fields.Nested('NeteaseSongSchema'))

    @post_load
    def create_model(self, data):
        return NArtistModel(**data)


class NeteasePlaylistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    desc = fields.Str(required=True, allow_none=True, load_from='description')
    cover = fields.Url(required=True, load_from='coverImgUrl')
    # songs field maybe null, though it can't be null in model
    songs = fields.List(fields.Nested(NeteaseSongSchema),
                        load_from='tracks',
                        allow_none=True)

    @post_load
    def create_model(self, data):
        if data.get('songs') is None:
            data.pop('songs')
        else:
            # 这里 Artist 和 Album 的 picUrl 链接不对，
            # 这个链接指向的是一个网易云默认的灰色图片，
            # 我们将其设置为 None
            for song in data['songs']:
                if song.artists:
                    for artist in song.artists:
                        artist.cover = None
                if song.album:
                    song.album.cover = None
        if data.get('desc') is None:
            data.pop('desc')
        return NPlaylistModel(**data)


class NeteaseUserSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    playlists = fields.List(fields.Nested(NeteasePlaylistSchema))

    @post_load
    def create_model(self, data):
        return UserModel(**data)


from .models import NAlbumModel
from .models import NArtistModel
from .models import NPlaylistModel
from .models import NSongModel
