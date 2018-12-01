from fuocore.models import (
    BaseModel,
    SongModel,
    PlaylistModel,
    AlbumModel,
    ArtistModel,
    SearchModel,
)

from .provider import provider


class QQBaseModel(BaseModel):
    _api = provider.api
    _detail_fields = ()

    class Meta:
        provider = provider

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



def _deserialize(data, schema_cls):
    schema = schema_cls(strict=True)
    obj, _ = schema.load(data)
    return obj


class QQSongModel(SongModel, QQBaseModel):

    class Meta:
        fields = ('mid', )

    @property
    def url(self):
        if self._url is not None:
            return self._url
        url = self._api.get_song_url(self.mid)
        if url is not None:
            self._url = url
        else:
            self._url = ''
        return self._url

    @url.setter
    def url(self, url):
        self._url = url


class QQAlbumModel(AlbumModel, QQBaseModel):
    _detail_fields = ('songs', 'desc')

    @classmethod
    def get(cls, identifier):
        data_album = cls._api.album_detail(identifier)
        album = _deserialize(data_album, QQAlbumSchema)
        return album

class QQArtistModel(ArtistModel, QQBaseModel):
    _detail_fields = ('songs', 'desc')

    class Meta:
        allow_get = True

    @classmethod
    def get(cls, identifier):
        data_artist = cls._api.artist_detail(identifier)
        artist = _deserialize(data_artist, QQArtistSchema)
        return artist


class QQPlaylistModel(PlaylistModel, QQBaseModel):
    pass


class QQSearchModel(SearchModel, QQBaseModel):
    pass


def search(keyword, **kwargs):
    data_songs = provider.api.search(keyword)
    songs = []
    for data_song in data_songs:
        song = _deserialize(data_song, QQSongSchema)
        songs.append(song)
    return QQSearchModel(songs=songs)


from .schemas import (
    QQArtistSchema,
    QQAlbumSchema,
    QQSongSchema,
)  # noqa
