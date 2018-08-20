from marshmallow import Schema as _Schema, fields, post_load


SOURCE = 'xiami'


class Schema(_Schema):
    source = fields.Str(missing=SOURCE)


class ArtistSchema(Schema):
    """歌手详情 Schema、歌曲歌手简要信息 Schema
    """

    identifier = fields.Int(load_from='artistId')
    name = fields.Str(load_from='artistName')
    cover = fields.Str(load_from='artistLogo', missing=None)
    desc = fields.Str(load_from='description', missing=None)

    @post_load
    def create_model(self, data):
        return XArtistModel(**data)


class AlbumSchema(Schema):
    """专辑详情 Schema

    >>> import json
    >>> with open('data/fixtures/xiami/album.json') as f:
    ...     data = json.load(f)
    ...     schema = AlbumSchema(strict=True)
    ...     album, _ = schema.load(data)
    >>> album.identifier
    2100387382
    """
    identifier = fields.Int(load_from='albumId')
    name = fields.Str(load_from='albumName')
    cover = fields.Str(load_from='albumLogo')

    songs = fields.List(fields.Nested('NestedSongSchema'))
    artists = fields.List(fields.Nested(ArtistSchema), load_from='singerVOs')
    desc = fields.Str(load_from='description')

    @post_load
    def create_model(self, data):
        return XAlbumModel(**data)


class SongSchema(Schema):
    """歌曲详情 Schema

    >>> import json
    >>> with open('data/fixtures/xiami/song.json') as f:
    ...     data = json.load(f)
    ...     schema = SongSchema(strict=True)
    ...     song, _ = schema.load(data)
    >>> song.url
    ''
    """
    identifier = fields.Str(load_from='songId')
    title = fields.Str(load_from='songName')
    duration = fields.Str(load_from='length')

    url = fields.Str(load_from='listenFile', missing='')
    # files = fields.List(fields.Dict, load_from='listenFiles', missing=[])

    artists = fields.List(fields.Nested(ArtistSchema), load_from='singerVOs')

    album_id = fields.Str(load_from='albumId')
    album_name = fields.Str(load_from='albumName')
    album_cover = fields.Str(load_from='albumLogo')

    @post_load
    def create_model(self, data):
        album = XAlbumModel(identifier=data['album_id'],
                            name=data['album_name'],
                            cover=data['album_cover'])
        # files = data['files']
        # files = sorted(files, key=lambda f: f['quality'], reverse=True)
        # if files:
        #     url = files[0]['url']
        # else:
        #     url = ''  # 设置为空，代表这首歌没有合适的 url
        song = XSongModel(identifier=data['identifier'],
                          title=data['title'],
                          url=data['url'],
                          duration=int(data['duration']),
                          album=album,
                          artists=data['artists'])
        return song


class NestedSongSchema(SongSchema):
    """搜索结果中歌曲 Schema、专辑/歌手详情中歌曲 Schema

    通过 search 得到的 Song 的结构和通过 song_detail 获取的 Song 的结构不一样

    search 接口得到的 Song 没有 listenFile 字段，但是可能会有 listenFiles 字段，
    有的话，取 listenFiles 中最高质量的播放链接作为音乐的 url。
    """
    files = fields.List(fields.Dict, load_from='listenFiles', missing=[])

    @post_load
    def create_model(self, data):
        song = super().create_model(data)
        files = sorted(data['files'], key=lambda f: f['quality'], reverse=True)
        if files:
            url = files[0]['listenFile']
        else:
            url = ''  # 设置为空，代表这首歌没有合适的 url
        song.url = url
        return song


class PlaylistSchema(Schema):
    """歌单 Schema

    >>> import json
    >>> with open('data/fixtures/xiami/playlist.json') as f:
    ...     data = json.load(f)
    ...     schema = PlaylistSchema(strict=True)
    ...     playlist, _ = schema.load(data)
    >>> len(playlist.songs)
    100
    """
    identifier = fields.Str(load_from='listId')
    name = fields.Str(load_from='collectName')
    cover = fields.Str(load_from='collectLogo')
    songs = fields.List(fields.Nested(NestedSongSchema))
    desc = fields.Str(load_from='description')

    @post_load
    def create_model(self, data):
        return XPlaylistModel(**data)


class SongSearchSchema(Schema):
    """歌曲搜索结果 Schema"""
    songs = fields.List(fields.Nested(NestedSongSchema))

    @post_load
    def create_model(self, data):
        return XSearchModel(**data)


from .models import (
    XAlbumModel,
    XArtistModel,
    XPlaylistModel,
    XSongModel,
    XSearchModel,
)  # noqa
