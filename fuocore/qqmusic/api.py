import base64
import re
import os
import json
import logging
from difflib import SequenceMatcher

import requests

logger = logging.getLogger(__name__)

api_base_url = 'http://c.y.qq.com'


class API(object):
    def __init__(self):
        super().__init__()
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'c.y.qq.com',
            'Referer': 'http://y.qq.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/64.0.3282.186 Safari/537.36'
        }
        self._cookies = dict(vkey='')
        self._http = None

    @property
    def cookies(self):
        return self._cookies

    def load_cookies(self, cookies):
        self._cookies.update(cookies)

    def refresh_cookies(self):
        action = api_base_url + '/base/fcgi-bin/fcg_music_express_mobile3.fcg'
        data = {
            'loginUin': 123456,
            'format': 'json',
            'cid': 205361747,
            'uin': 123456,
            'songmid': '003a1tne1nSz1Y',
            'filename': 'C400003a1tne1nSz1Y.m4a',
            'guid': 10000
        }
        res_data = self.request("GET", action, data)
        self._cookies.update({'vkey': res_data['items'][0]['vkey']})

    def set_http(self, http):
        self._http = http

    @property
    def http(self):
        return requests if self._http is None else self._http

    def request(self, method, action, query=None, timeout=3):
        try:
            if method == "GET":
                res = self.http.get(action, params=query,
                                    headers=self._headers, timeout=timeout)
            if res is not None:
                content_str = res.text
                try:
                    content_dict = json.loads(content_str)
                except:
                    content_dict = json.loads(re.match(".*?({.*}).*", content_str, re.S).group(1))
                try:
                    return content_dict['data']
                except:
                    return content_dict
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    # 搜索歌曲(1),专辑(10),歌手(100),歌单(1000) *(type)*
    def _search_songs(self, keywords, page, limit):
        action = api_base_url + '/soso/fcgi-bin/client_search_cp'
        data = {
            'w': keywords,
            't': 0,
            'cr': 1,
            'p': page,
            'n': limit,
            'format': 'json'
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['song']['totalnum'],
                'next': page + 1
            }
            return res_data['song']['list'], info
        except Exception as e:
            logger.error(str(e))
            return None

    def _search_albums(self, keywords, page, limit):
        action = api_base_url + '/soso/fcgi-bin/client_search_cp'
        data = {
            'w': keywords,
            't': 8,
            'cr': 1,
            'p': page,
            'n': limit,
            'format': 'json'
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['album']['totalnum'],
                'next': page + 1
            }
            return res_data['album']['list'], info
        except Exception as e:
            logger.error(str(e))
            return None

    def _search_artists(self, keywords, page, limit):
        action = api_base_url + '/soso/fcgi-bin/client_search_cp'
        data = {
            'w': keywords,
            't': 9,
            'cr': 1,
            'p': page,
            'n': limit,
            'format': 'json'
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['singer']['totalnum'],
                'next': page + 1
            }
            return res_data['singer']['list'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_playlists(self, keywords, page, limit):
        action = api_base_url + '/soso/fcgi-bin/client_music_search_songlist'
        data = {
            'query': keywords,
            'page_no': page - 1,
            'num_per_page': limit,
            'format': 'jsonp'
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['sum'],
                'next': page + 1
            }
            return res_data['list'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def search(self, keywords, type=1, page=1, limit=30):
        if type == 1:
            return self._search_songs(keywords, page, limit)
        elif type == 10:
            return self._search_albums(keywords, page, limit)
        elif type == 100:
            return self._search_artists(keywords, page, limit)
        elif type == 1000:
            return self._search_playlists(keywords, page, limit)
        else:
            return [], None

    # 歌曲详情 歌曲地址 歌曲歌词
    def song_detail(self, song_id):
        action = api_base_url + '/v8/fcg-bin/fcg_play_single_song.fcg'
        data = {
            'songmid': song_id,
            'format': 'json'
        }
        res_data = self.request("GET", action, data)
        try:
            return res_data[0]
        except Exception as e:
            logger.error(str(e))
            return None

    def songs_url(self, media_ids, quality='M800'):  # F000(flac) A000(ape) M800(320) M500(128) C400(192)
        switcher = {
            'F000': 'flac',
            'A000': 'ape',
            'C400': 'm4a'
        }
        if self.cookies['vkey'] is '':
            self.refresh_cookies()
        songs_url = []
        for media_id in media_ids:
            filename = '{}{}.{}'.format(
                quality, media_id, switcher.get(quality, 'mp3'))
            songs_url.append('http://streamoc.music.tc.qq.com/{}?vkey={}&guid={}&uin={}&fromtag={}'.format(
                filename, self.cookies['vkey'], 10000, 123456, 8))
        return songs_url

    def song_lyrics(self, song_id):
        action = api_base_url + '/lyric/fcgi-bin/fcg_query_lyric_new.fcg'
        data = {
            'songmid': song_id,
            'format': 'jsonp'
        }
        res_data = self.request("GET", action, data)
        try:
            return base64.b64decode(res_data['lyric']).decode('utf-8')
        except Exception as e:
            logger.error(str(e))
            return ''

    # 专辑详情
    def album_detail(self, album_id):
        action = api_base_url + '/v8/fcg-bin/fcg_v8_album_info_cp.fcg'
        data = {
            'albummid': album_id,
            'format': 'json'
        }
        res_data = self.request("GET", action, data)
        return res_data

    # 歌手详情 歌手专辑
    def artist_detail(self, artist_id, page=1, limit=30):
        action = api_base_url + '/v8/fcg-bin/fcg_v8_singer_track_cp.fcg'
        data = {
            'singermid': artist_id,
            'order': 'listen',
            'begin': page - 1,
            'num': limit,
            'from': 'h5'
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['total'],
                'next': page + 1
            }
            if page > 1:
                return res_data['list'], info
            else:
                return res_data, info
        except Exception as e:
            logger.error(str(e))
            if page > 1:
                return [], None
            else:
                return None, None

    def artist_albums(self, artist_id, page=1, limit=30):
        action = api_base_url + '/v8/fcg-bin/fcg_v8_singer_album.fcg'
        data = {
            'singermid': artist_id,
            'order': 'time',
            'begin': page - 1,
            'num': limit
        }
        res_data = self.request("GET", action, data)
        try:
            info = {
                'more': page * limit < res_data['total'],
                'next': page + 1
            }
            return res_data['list'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    # 歌单详情
    def playlist_detail(self, playlist_id):
        action = api_base_url + '/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg'
        data = {
            'disstid': playlist_id,
            'type': 1,
            'format': 'jsonp'
        }
        res_data = self.request("GET", action, data)
        try:
            return res_data['cdlist'][0]
        except Exception as e:
            logger.error(str(e))
            return None

    # 提供给其他模块(网易云、虾米)调用的外链搜索
    def search_url(self, title, artist_name, duration=0):
        songs, info = self.search(title + artist_name)
        if not songs:
            return ''
        target_song = None
        max_match_ratio = 0.5
        max_duration_difference = 5000
        for song in songs:
            if song['songname'].lower() == title.lower():
                ratio = SequenceMatcher(None, song['singer'][0]['name'], artist_name).ratio()
                difference = abs(duration - song['interval'] * 1000) if duration else 0
                if (ratio > max_match_ratio) and (difference < max_duration_difference):
                    target_song = song
                    if ratio == 1:
                        break
                    max_match_ratio = ratio
        if target_song is not None:
            return self.songs_url([target_song['media_mid']])[0]
        else:
            return ''

    # 提供给本模块(QQ音乐)调用的获取外链搜索
    def get_3rd_url(self, title, artist_name, duration):
        try:
            from fuocore.xiami.api import api as xiami_assister
            cookie_file = os.path.expanduser('~') + '/.FeelUOwn/data/xmm_users_info.json'
            if os.path.exists(cookie_file):
                users_info = json.load(open(cookie_file))
                cookies = list(users_info.values())[0]['cookies']
                xiami_assister.load_cookies(cookies)
            target_url = xiami_assister.search_url(title, artist_name, duration)
            if target_url is not '':
                return target_url
        except Exception as e:
            logger.error(str(e))
        try:
            from fuocore.netease.api import api as netease_assister
            cookie_file = os.path.expanduser('~') + '/.FeelUOwn/data/nem_users_info.json'
            if os.path.exists(cookie_file):
                users_info = json.load(open(cookie_file))
                cookies = list(users_info.values())[0]['cookies']
                netease_assister.load_cookies(cookies)
            target_url = netease_assister.search_url(title, artist_name, duration)
            if target_url is not '':
                return target_url
        except Exception as e:
            logger.error(str(e))
        return ''


api = API()
