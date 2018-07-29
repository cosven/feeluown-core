from fuocore.models import (
    BaseModel,
    SongModel,
    LyricModel,
    PlaylistModel,
    AlbumModel,
    ArtistModel,
    SearchModel,
    UserModel,
)

from .provider import provider


class QQBaseModel(BaseModel):
    _provider = provider
    api = provider.api

    _detail_fields = ()

    @classmethod
    def get(cls, identifier):
        raise NotImplementedError

    def __getattribute__(self, name):
        cls = type(self)
        value = object.__getattribute__(self, name)
        if name in cls._detail_fields and not value:
            obj = cls.get(self.identifier)
            for field in cls._detail_fields:
                setattr(self, field, getattr(obj, field))
            value = object.__getattribute__(self, name)
        return value


class QQSongModel(SongModel, QQBaseModel):

    class Meta:
        fields = ('mid', )

    @property
    def url(self):
        if self._url is not None:
            return self._url
        url = self.api.get_song_url(self.mid)
        if url is not None:
            self._url = url
        else:
            self._url = ''
        return self._url

    @url.setter
    def url(self, url):
        self._url = url


class QQAlbumModel(AlbumModel, QQBaseModel):
    pass


class QQArtistModel(ArtistModel, QQBaseModel):
    pass


class QQPlaylistModel(PlaylistModel, QQBaseModel):
    pass


class QQSearchModel(SearchModel, QQBaseModel):
    pass


def search(keyword, **kwargs):
    data_songs = provider.api.search(keyword)
    songs = []
    for data_song in data_songs:
        album = QQAlbumModel(identifier=data_song['albumid'],
                             name=data_song['albumname'])
        artists = []
        for data_artist in data_song['singer']:
            artist = QQArtistModel(identifier=data_artist['id'],
                                   name=data_artist['name'])
            artists.append(artist)
        song = QQSongModel(identifier=data_song['songid'],
                           source=provider.identifier,
                           mid=data_song['songmid'],
                           title=data_song['songname'],
                           duration=data_song['interval'] * 1000,
                           album=album,
                           artists=artists)
        songs.append(song)
    return QQSearchModel(songs=songs)
