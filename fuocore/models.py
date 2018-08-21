# -*- coding: utf-8 -*-

"""
fuocore.model
~~~~~~~~~~~~~

这个模块对音乐相关模型进行了定义，声明了各模型的属性。
"""

from enum import IntEnum


class ModelType(IntEnum):
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
                 fields=None,
                 allow_get=False,
                 allow_batch=False,
                 **kwargs):
        """Model metadata class

        :param allow_get: if get method is implemented
        :param allow_batch: if list method is implemented
        """
        self.model_type = model_type
        self.provider = provider
        self.fields = fields
        self.allow_get = allow_get
        self.allow_batch = allow_batch
        for key, value in kwargs.items():
            setattr(self, key, value)


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        # get all meta
        _metas = []
        for base in bases:
            base_meta = getattr(base, '_meta', None)
            if base_meta is not None:
                _metas.append(base_meta)

        # similar with djang/peewee model meta
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
        """获取 Model 详细信息

        NOTE: 字段值如果是 None 的话，说明之前这个字段没有被初始化过。
        所以在调用 get 接口之后，需要将每个字段初始化为非 None。
        """
        raise NotImplementedError

    @classmethod
    def list(cls, identifier_list):
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

        # TODO: 之后可能需要给 Album 多加一个字段用来分开表示 artist 和 singer
        # 从意思上来区分的话：artist 是专辑制作人，singer 是演唱者
        # 像虾米音乐中，它即提供了专辑制作人信息，也提供了 singer 信息
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
        # TODO: 支持低/中/高不同质量的音乐文件
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

        # XXX: songs should be a empty list instead of None
        # when there is not song.
        fields = ['q', 'songs']

    def __str__(self):
        return 'fuo://{}?q={}'.format(self.source, self.q)


class UserModel(BaseModel):
    """
    playlists: 创建的歌单
    fav_playlists: 收藏的歌单
    """
    class Meta:
        model_type = ModelType.user.value
        fields = ['name', 'playlists', 'fav_playlists']
