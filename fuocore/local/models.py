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

    def __getattribute__(self, name):
        cls = type(self)
        value = object.__getattribute__(self, name)
        if name in cls._detail_fields and value is None:
            logger.debug('Field %s value is None, get model detail first.' % name)
            obj = cls.get(self.identifier)
            for field in cls._detail_fields:
                setattr(self, field, getattr(obj, field))
            value = object.__getattribute__(self, name)
        elif name in cls._detail_fields and not value:
            logger.debug('Field %s value is not None, but is %s' % (name, value))
        return value


class LSongModel(SongModel, LBaseModel):

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
