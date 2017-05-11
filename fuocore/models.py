# -*- coding: utf-8 -*-

from april import Model
from april.tipes import listof


class BriefArtistModel(Model):
    name = str
    img = str

    _optional_fields = ['img']


class BriefAlbumModel(Model):
    name = str
    artists = listof(BriefArtistModel)
    img = str


class BriefSongModel(Model):
    name = str
    duration = int
    album = BriefAlbumModel
    artists = BriefArtistModel
    source = str

    @classmethod
    def search(cls, name):
        pass


class ArtistModel(BriefArtistModel):
    hot_songs = listof(BriefSongModel)
    desc = str

    _optional_fields = ('desc')


class AlbumModel(BriefAlbumModel):
    songs = listof(BriefSongModel)
    desc = str

    _optional_fields = ('desc')


class LyricModel(Model):
    song = BriefSongModel
    content = str
    trans_content = str

    _optional_fields = ('trans_content')


class SongModel(BriefSongModel):
    url = str
