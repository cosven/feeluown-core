import logging

from fuocore.models import (
    BaseModel,
    SongModel,
    AlbumModel,
    ArtistModel,
    SearchModel,
)

from .provider import provider

logger = logging.getLogger(__name__)


class LBaseModel(BaseModel):
    _detail_fields = ()

    class Meta:
        allow_get = True
        provider = provider


class LSongModel(SongModel, LBaseModel):
    class Meta:
        fields_no_get = ('lyric', )

    @classmethod
    def get(cls, identifier):
        return cls.meta.provider.library._songs.get(identifier)

    @classmethod
    def list(cls, identifier_list):
        return map(cls.meta.provider.library._songs.get, identifier_list)


class LAlbumModel(AlbumModel, LBaseModel):
    _detail_fields = ('songs',)

    @classmethod
    def get(cls, identifier):
        return cls.meta.provider.library._albums.get(identifier)


class LArtistModel(ArtistModel, LBaseModel):
    _detail_fields = ('songs',)

    @classmethod
    def get(cls, identifier):
        return cls.meta.provider.library._artists.get(identifier)


class LSearchModel(SearchModel, LBaseModel):
    pass
