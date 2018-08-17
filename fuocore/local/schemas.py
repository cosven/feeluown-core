# -*- coding: utf-8 -*-
import base64

from marshmallow import Schema, post_load, fields

from fuocore.schemas import SongSchema
from fuocore.utils import elfhash

SOURCE = 'local'


class EasyMP3MetadataSongSchema(Schema):
    """EasyMP3 metadata"""
    url = fields.Str(required=True)
    title_list = fields.List(fields.Str(), load_from='title', required=True)
    duration = fields.Float(required=True)
    artist_name_list = fields.List(fields.Str(), load_from='artist')
    album_name_list = fields.List(fields.Str(), load_from='album')

    @post_load
    def create_song_model(self, data):
        title_list = data.get('title_list', [])
        title = title_list[0] if title_list else 'Unknown'
        album_name_list = data.get('album_name_list', [])
        artist_name_list = data.get('artist_name_list', [])
        if len(artist_name_list) > 0:
            # 通过调研正确区分是否需要这部操作?还是','或'/'分隔符号还是都用(可能用'/'最靠谱?)
            artist_name_list = [artist.strip() for artist in artist_name_list[0].split('&')]
        identifier = str(elfhash(base64.b64encode(bytes(data['url'], 'utf-8'))))
        # 后期iTunes AAC的支持(因为港台购买的音乐只要是繁体)
        # 歌曲信息强制简繁体转换(用户可以自由设置显示的语言和下载保存的语言)
        song_data = {
            'source': SOURCE,
            'identifier': identifier,
            'title': title,
            'duration': data['duration'],
            'url': data['url'],
        }
        if album_name_list:
            identifier = str(elfhash(base64.b64encode(bytes(album_name_list[0], 'utf-8'))))
            song_data['album'] = {'identifier': identifier,#后期将利用专辑和专辑艺术家的组合来确定(注意是专辑艺术家不是歌曲艺术家)
                                  'source': SOURCE,
                                  'name': album_name_list[0]}
        song_data['artists'] = []
        if artist_name_list:
            for name in artist_name_list:
                identifier = str(elfhash(base64.b64encode(bytes(name, 'utf-8'))))
                song_data['artists'].append({'identifier': identifier,
                                             'source': SOURCE,
                                             'name': name})
        song, _ = SongSchema(strict=True).load(song_data)
        return song
