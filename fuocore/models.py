# -*- coding: utf-8 -*-

import uuid

from april import Model
from april.tipes import listof
from april.utils import is_nested_type


class BaseModel(Model):

    _source = None

    @property
    def identifier(self):
        """the model indentifier (unique)"""
        if hasattr(self, '_identifier'):
            return self._identifier
        self._identifier = uuid.uuid1().hex
        return self._identifier

    @property
    def source(self):
        if self._source is None:
            raise NotImplementedError()
        return self._source

    @source.setter
    def source(self, value):
        """set source for model and model's field recursively"""
        self._source = value
        for name, ftype in self._fields:
            if issubclass(ftype, BaseModel):
                setattr(getattr(self, name), 'source', value)
            if is_nested_type(ftype):
                # FIXME: wait for ``april`` redesigning nested type interface
                for each in getattr(self, name):
                    setattr(each, 'source', value)

    def __eq__(self, other):
        if hasattr(other, 'identifier'):
            return self.identifier == other.identifier
        return False

    def __ne__(self, other):
        if hasattr(other, 'identifier'):
            return self != other
        return True


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
        if not hasattr(self, 'brief_artists'):
            return self.name + ' - unknown'
        module = type(self).__module__
        class_name = type(self).__name__
        song_name = self.name + ' - ' + \
            ', '.join([artist.name for artist in self.brief_artists])
        source = self.source
        return '<{module}.{class_name} {song_name} {source}>'.format(**locals())


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
