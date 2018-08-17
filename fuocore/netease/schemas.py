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
    album = fields.Nested('NeteaseAlbumSchema',allow_none=True)
    artists = fields.List(fields.Nested('NeteaseArtistSchema'),allow_none=True)

    @post_load
    def create_model(self, data):
        if 'album' in data:
            # 需要保留cover以显示出来
            # data['album'].cover = None
            data['album'].songs = None
            data['album'].artists = None
        if 'artists' in data:
            for artist in data['artists']:
                artist.cover = None
                artist.songs = None
                artist.albums = None
        return NSongModel(**data)


class NeteaseAlbumSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    cover = fields.Str(load_from='picUrl', allow_none=True)
    songs = fields.List(fields.Nested(NeteaseSongSchema), allow_none=True)
    artists = fields.List(fields.Nested('NeteaseArtistSchema'), allow_none=True)

    @post_load
    def create_model(self, data):
        if 'songs' in data:
            for song in data['songs']:
                if song.artists:
                    for artist in song.artists:
                        artist.cover = None
                        artist.songs = None
                        artist.albums = None
                if song.album:
                    song.album.cover = None
                    song.album.songs = None
                    song.album.artists = None
        if 'artists' in data:
            for artist in data['artists']:
                artist.cover = None
                artist.songs = None
                artist.albums = None
        return NAlbumModel(**data)


class NeteaseArtistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str()
    cover = fields.Str(load_from='picUrl', allow_none=True)
    songs = fields.List(fields.Nested(NeteaseSongSchema), allow_none=True)
    albums = fields.List(fields.Nested(NeteaseAlbumSchema), allow_none=True)

    @post_load
    def create_model(self, data):
        if 'songs' in data:
            for song in data['songs']:
                if song.artists:
                    for artist in song.artists:
                        artist.cover = None
                        artist.songs = None
                        artist.albums = None
                if song.album:
                    song.album.cover = None
                    song.album.songs = None
                    song.album.artists = None
        if 'albums' in data:
            for album in data['albums']:
                # 需要保留cover以显示出来
                # album.cover = None
                album.songs = None
                album.artists = None
        return NArtistModel(**data)


class NeteasePlaylistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    uid = fields.Int(required=True, load_from='userId')
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
            # 通过user调用的时候为空,需要pop掉(特殊情况,playlists本身为空)
            data.pop('songs')
        else:
            # song.album.songs 这里会返回空列表，设置为 None
            for song in data['songs']:
                if song.artists:
                    for artist in song.artists:
                        artist.cover = None
                        artist.songs = None
                        artist.albums = None
                if song.album:
                    song.album.cover = None
                    song.album.songs = None
                    song.album.artists = None
        if data.get('desc') is None:
            data.pop('desc')
        return NPlaylistModel(**data)


class NeteaseUserSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    cover = fields.Str(allow_none=True)
    cookies = fields.Dict()
    playlists = fields.List(fields.Nested(NeteasePlaylistSchema))
    fav_songs = fields.List(fields.Nested(NeteaseSongSchema))
    fav_albums = fields.List(fields.Nested(NeteaseAlbumSchema))
    fav_artists = fields.List(fields.Nested(NeteaseArtistSchema))
    fav_playlists = fields.List(fields.Nested(NeteasePlaylistSchema))

    @post_load
    def create_model(self, data):
        return NUserModel(**data)


from .models import NAlbumModel
from .models import NArtistModel
from .models import NPlaylistModel
from .models import NSongModel
from .models import NUserModel
