# -*- coding: utf-8 -*-

import uuid

from april import Model
from april.tipes import listof


class BaseModel(Model):
    #: mark this model's provider
    source = str

    @property
    def identifier(self):
        """the model indentifier (unique)"""
        if hasattr(self, '_identifier'):
            return self._identifier
        self._identifier = uuid.uuid1().hex
        return self._identifier

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __ne__(self, other):
        return self != other


class BriefArtistModel(BaseModel):
    name = str
    img = str

    _optional_fields = ['img']


class BriefAlbumModel(BaseModel):
    name = str


class BriefSongModel(BaseModel):

    name = str
    url = str
    duration = int
    brief_album = BriefAlbumModel
    brief_artists = listof(BriefArtistModel)

    _optional_fields = ['url', 'duration', 'brief_album', 'brief_artists']

    def __str__(self):
        return self.name + ' - ' + \
                ', '.join([artist.name for artist in self.brief_artists])


class ArtistModel(BriefArtistModel):
    songs = listof(BriefSongModel)
    desc = str

    _optional_fields = ('desc', )


class AlbumModel(BriefAlbumModel):
    img = str
    brief_songs = listof(BriefSongModel)
    brief_artists = listof(BriefArtistModel)
    desc = str

    _optional_fields = ('desc', )


class LyricModel(Model):
    song = BriefSongModel
    content = str
    trans_content = str

    _optional_fields = ('trans_content', )


class SongModel(BriefSongModel):

    _optional_fields = ['duration', 'brief_album', 'brief_artists',
                        'album', 'artists']
