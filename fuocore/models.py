# -*- coding: utf-8 -*-


from april import Struct


class BaseModel(Struct):
    _fields = ['source', 'identifier']


class BriefArtistModel(BaseModel):
    _fields = ['name', 'img']


class BriefAlbumModel(BaseModel):
    _fields = ['name']


class BriefSongModel(BaseModel):
    _fields = ['title', 'url', 'duration', 'brief_album', 'brief_artists']


class ArtistModel(BriefArtistModel):
    _fields = ['songs', 'desc']

    def __str__(self):
        return 'fuo://{}/artists/{}'.format(self.source, self.identifier)


class AlbumModel(BriefAlbumModel):
    _fields = ['img', 'songs', 'artists', 'desc']

    def __str__(self):
        return 'fuo://{}/albums/{}'.format(self.source, self.identifier)


class LyricModel(BaseModel):
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
    _fields = ['name', 'cover', 'songs']

    def __str__(self):
        return 'fuo://{}/playlists/{}'.format(self.source, self.identifier)


class UserModel(BaseModel):
    _fields = ['name', 'playlists']
