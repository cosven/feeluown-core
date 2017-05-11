# -*- coding: utf-8 -*-

from april import Model
from april.tipes import listof


class BaseModel(Model):
    source = str


class BriefArtistModel(BaseModel):
    name = str
    img = str

    _optional_fields = ['img']


class BriefAlbumModel(BaseModel):
    name = str


class BriefSongModel(BaseModel):
    name = str
    duration = int
    brief_album = BriefAlbumModel
    brief_artists = listof(BriefArtistModel)

    @classmethod
    def search(cls, name):
        pass


class ArtistModel(BriefArtistModel):
    hot_songs = listof(BriefSongModel)
    desc = str

    _optional_fields = ('desc', )


class AlbumModel(BriefAlbumModel):
    img = str
    songs = listof(BriefSongModel)
    artists = listof(BriefArtistModel)
    desc = str

    _optional_fields = ('desc', )


class LyricModel(Model):
    song = BriefSongModel
    content = str
    trans_content = str

    _optional_fields = ('trans_content', )


class SongModel(BriefSongModel):
    url = str
