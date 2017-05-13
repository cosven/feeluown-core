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
        raise NotImplementedError


class BriefArtistModel(BaseModel):
    name = str
    img = str

    _optional_fields = ['img']

    @property
    def identifier(self):
        return uuid.uuid1().hex


class BriefAlbumModel(BaseModel):
    name = str

    @property
    def identifier(self):
        return uuid.uuid1().hex


class BriefSongModel(BaseModel):
    name = str
    url = str
    duration = int
    brief_album = BriefAlbumModel
    brief_artists = listof(BriefArtistModel)

    _optional_fields = ['url', 'duration', 'brief_album', 'brief_artists']

    @property
    def identifier(self):
        return uuid.uuid1().hex


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
    url = str

    _optional_fields = ['duration', 'brief_album', 'brief_artists',
                        'album', 'artists']
