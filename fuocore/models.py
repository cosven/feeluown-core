# -*- coding: utf-8 -*-

from enum import Enum

from april import Struct


class ModelType(Enum):
    dummy = 0

    song = 1
    artist = 2
    album = 3
    playlist = 4
    lyric = 5

    user = 17


class BaseModel(Struct):
    type_ = ModelType.dummy
    _fields = ['source', 'identifier']


    def __eq__(self, other):
        if not isinstance(other, BaseModel):
            return False
        return all([other.source == self.source,
                    other.identifier == self.identifier,
                    other.type_ == self.type_])


class BriefArtistModel(BaseModel):
    type_ = ModelType.artist
    _fields = ['name', 'cover']


class BriefAlbumModel(BaseModel):
    type_ = ModelType.album
    _fields = ['name']


class BriefSongModel(BaseModel):
    type_ = ModelType.song
    _fields = ['title', 'url', 'duration', 'brief_album', 'brief_artists']


class ArtistModel(BriefArtistModel):
    _fields = ['songs', 'desc']

    def __str__(self):
        return 'fuo://{}/artists/{}'.format(self.source, self.identifier)


class AlbumModel(BriefAlbumModel):
    _fields = ['cover', 'songs', 'artists', 'desc']

    def __str__(self):
        return 'fuo://{}/albums/{}'.format(self.source, self.identifier)


class LyricModel(BaseModel):
    type_ = ModelType.lyric
    _fields = ['song', 'content', 'trans_content']


class SongModel(BriefSongModel):
    _fields = ['album', 'artists', 'lyric', 'comments']

    @property
    def artists_name(self):
        return ','.join((artist.name for artist in self.artists))

    @property
    def album_name(self):
        return self.album.name if self.album is not None else ''

    @property
    def filename(self):
        return '{} - {}.mp3'.format(self.title, self.artists_name)

    def __str__(self):
        return 'fuo://{}/songs/{}'.format(self.source, self.identifier)  # noqa

    def __eq__(self, other):
        return all([other.source == self.source,
                    other.identifier == self.identifier])


class PlaylistModel(BaseModel):
    type_ = ModelType.playlist
    _fields = ['name', 'cover', 'songs', 'desc']

    def __str__(self):
        return 'fuo://{}/playlists/{}'.format(self.source, self.identifier)


class UserModel(BaseModel):
    type_ = ModelType.user
    _fields = ['name', 'playlists']
