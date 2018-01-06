from marshmallow import Schema, post_load, fields

from fuocore.schemas import (
    AlbumSchema,
    ArtistSchema,
    PlaylistSchema,
    SongSchema,
    UserSchema,
)
from fuocore.netease.models import NSongModel

SOURCE = 'netease'


# NOTE: these BriefXxxSchema are used to support NeteaseXxxSchema
# FIXME: remove some of them to make code clean
class BriefAlbumSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    name = fields.Str(required=True)


class BriefArtistSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    name = fields.Str(required=True)


class BriefSongSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    title = fields.Str(required=True, load_from='name')
    url = fields.Str()
    duration = fields.Float(required=True)


class BriefPlaylistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)


class NeteaseSongSchema(Schema):
    identifier = fields.Int(requried=True, load_from='id')
    title = fields.Str(required=True, load_from='name')
    duration = fields.Float(required=True)
    url = fields.Str()
    album = fields.Nested(BriefAlbumSchema, required=True)
    artists = fields.List(fields.Nested(BriefArtistSchema), required=True)

    @post_load
    def create_model(self, data):
        # FIXME: improve code style if possible
        album = data['album']
        album['source'] = SOURCE
        artists = data['artists']
        for artist in artists:
            artist['source'] = SOURCE
        data['source'] = SOURCE
        data['album'] = album
        data['artists'] = artists
        # we can temporarily set url to ''
        if 'url' not in data:
            data['url'] = ''
        # make sure this is compatible with SongSchema
        song, _ = SongSchema(strict=True).load(data)
        return NSongModel(song)


class NeteaseAlbumSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str()
    img = fields.Str(load_from='picUrl')
    songs = fields.List(fields.Nested(BriefSongSchema), required=True)
    artists = fields.List(fields.Nested(BriefArtistSchema), required=True)

    @post_load
    def create_model(self, data):
        data['source'] = SOURCE
        for song in data['songs']:
            song['source'] = SOURCE
        for artist in data['artists']:
            artist['source'] = SOURCE
        album, _ = AlbumSchema(strict=True).load(data)
        return album


class NeteaseArtistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str()
    img = fields.Str(load_from='picUrl')
    songs = fields.List(fields.Nested(BriefSongSchema), required=True)

    @post_load
    def create_model(self, data):
        data['source'] = SOURCE
        artist, _ = ArtistSchema(strict=True).load(data)
        return artist


class NeteasePlaylistSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    # songs field maybe null
    songs = fields.List(fields.Nested(BriefSongSchema),
                        load_from='tracks',
                        allow_none=True)

    @post_load
    def create_model(self, data):
        data['source'] = SOURCE
        if data.get('songs') is None:
            data.pop('songs')
        else:
            for song in data['songs']:
                song['source'] = SOURCE
                # set url field to avoid ValidationError
                song['url'] = ''
        playlist, _ = PlaylistSchema(strict=True).load(data)
        return playlist


class NeteaseUserSchema(Schema):
    identifier = fields.Int(required=True, load_from='id')
    name = fields.Str(required=True)
    playlists = fields.List(fields.Nested(BriefPlaylistSchema))

    @post_load
    def create_model(self, data):
        data['source'] = SOURCE
        for playlist in data['playlists']:
            playlist['source'] = SOURCE
        user, _ = UserSchema(strict=True).load(data)
        return user
