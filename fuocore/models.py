# -*- coding: utf-8 -*-

from enum import Enum


class ModelType(Enum):
    dummy = 0

    song = 1
    artist = 2
    album = 3
    playlist = 4
    lyric = 5

    user = 17


_TYPE_NAME_MAP = {
    ModelType.song: 'Song',
    ModelType.artist: 'Artist',
    ModelType.album: 'Album',
    ModelType.playlist: 'Playlist',
    ModelType.lyric: 'Lyric',
    ModelType.user: 'User',
}


class ModelMetadata(object):
    def __init__(self,
                 model_type=ModelType.dummy.value,
                 provider=None,
                 fields=None):
        self.model_type = model_type
        self.provider = provider
        self.fields = fields


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        # get all meta
        _metas = []
        for base in bases:
            base_meta = getattr(base, '_meta', None)
            if base_meta is not None:
                _metas.append(base_meta)
        Meta = attrs.pop('Meta', None)
        if Meta:
            _metas.append(Meta)

        fields = list()
        meta_kv = {}
        for _meta in _metas:
            inherited_fields = getattr(_meta, 'fields', [])
            fields.extend(inherited_fields)
            for k, v in _meta.__dict__.items():
                if k.startswith('_') or k in ('fields', ):
                    continue
                if k == 'model_type':
                    if ModelType(v) != ModelType.dummy:
                        meta_kv[k] = v
                else:
                    meta_kv[k] = v

        klass = type.__new__(cls, name, bases, attrs)

        # update provider
        provider = meta_kv.pop('provider', None)
        model_type = meta_kv.pop('model_type', ModelType.dummy.value)
        if provider and ModelType(model_type) != ModelType.dummy:
            model_name = _TYPE_NAME_MAP[ModelType(model_type)]
            setattr(provider, model_name, klass)
        fields = list(set(fields))
        klass._meta = ModelMetadata(model_type=model_type,
                                    provider=provider,
                                    fields=fields,
                                    **meta_kv)
        return klass


class Model(object, metaclass=ModelMeta):
    """base class for data models
    Usage::

        class User(Model):
            class Meta:
                fields = ['name', 'title']
        user = UserModel(name='xxx')
        assert user.name == 'xxx'
        user2 = UserModel(user)
        assert user2.name = 'xxx'
    """

    def __init__(self, obj=None, **kwargs):
        for field in self._meta.fields:
            setattr(self, field, getattr(obj, field, None))

        for k, v in kwargs.items():
            if k in self._meta.fields:
                setattr(self, k, v)


class BaseModel(Model):
    class Meta:
        model_type = ModelType.dummy.value
        fields = ['source', 'identifier']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, BaseModel):
            return False
        return all([other.source == self.source,
                    other.identifier == self.identifier,
                    other._meta.model_type == self._meta.model_type])

    @classmethod
    def get(cls, identifier):
        raise NotImplementedError


class ArtistModel(BaseModel):
    class Meta:
        model_type = ModelType.artist.value
        fields = ['name', 'cover', 'songs', 'desc']

    def __str__(self):
        return 'fuo://{}/artists/{}'.format(self.source, self.identifier)


class AlbumModel(BaseModel):
    class Meta:
        model_type = ModelType.album.value
        fields = ['name', 'cover', 'songs', 'artists', 'desc']

    def __str__(self):
        return 'fuo://{}/albums/{}'.format(self.source, self.identifier)


class LyricModel(BaseModel):
    class Meta:
        model_type = ModelType.lyric.value
        fields = ['song', 'content', 'trans_content']


class SongModel(BaseModel):
    class Meta:
        model_type = ModelType.song.value
        fields = ['album', 'artists', 'lyric', 'comments', 'title', 'url',
                  'duration', ]

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
    class Meta:
        model_type = ModelType.playlist.value
        fields = ['name', 'cover', 'songs', 'desc']

    def __str__(self):
        return 'fuo://{}/playlists/{}'.format(self.source, self.identifier)

    def add_song(self, song_id, allow_exist=True):
        pass

    def remove_song(self, song_id, allow_not_exist=True):
        pass


class SearchModel(BaseModel):
    class Meta:
        model_type = ModelType.dummy.value
        fields = ['q', 'songs']

    def __str__(self):
        return 'fuo://{}?q={}'.format(self.source, self.q)


class UserModel(BaseModel):
    class Meta:
        model_type = ModelType.user.value
        fields = ['name', 'playlists', 'cookies', 'fav_playlists']
