import base64
import binascii
import re
import os
import json
import logging
from difflib import SequenceMatcher

from bs4 import BeautifulSoup
import urllib
import requests
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

site_uri = 'http://music.163.com'
uri = 'http://music.163.com/api'
uri_we = 'http://music.163.com/weapi'
uri_v1 = 'http://music.163.com/weapi/v1'

logger = logging.getLogger(__name__)


class API(object):
    """netease music api

    Simple usage::

        from fuocore import netease
        data = netease.search(u'sugar')
        songs = data['result']['songs']
    """

    # 函数初始化
    def __init__(self):
        super().__init__()
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/33.0.1750.152 Safari/537.36'
        }
        self._cookies = dict(appver="1.5.9", os="osx")
        self._http = None

    @property
    def cookies(self):
        return self._cookies

    def load_cookies(self, cookies):
        self._cookies.update(cookies)

    def set_http(self, http):
        self._http = http

    @property
    def http(self):
        return requests if self._http is None else self._http

    def request(self, method, action, query=None, timeout=3):
        # logger.info('method=%s url=%s data=%s' % (method, action, query))
        try:
            if method == "GET":
                res = self.http.get(action, headers=self._headers,
                                    cookies=self._cookies, timeout=timeout)
            elif method == "POST":
                res = self.http.post(action, data=query, headers=self._headers,
                                     cookies=self._cookies, timeout=timeout)
            elif method == "POST_UPDATE":
                res = self.http.post(action, data=query, headers=self._headers,
                                     cookies=self._cookies, timeout=timeout)
                self._cookies.update(res.cookies.get_dict())
            if res is not None:
                try:
                    content = res.content
                    content_str = content.decode('utf-8')
                    content_dict = json.loads(content_str)
                    return content_dict
                except:
                    return res
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    # 用户登陆
    def login(self, username, pw_encrypt, phone=False):
        action = uri_we + '/login?csrf_token='
        phone_action = uri_we + '/login/cellphone'
        data = {
            'password': pw_encrypt,
            'rememberLogin': 'true'
        }
        if username.isdigit() and len(username) == 11:
            phone = True
            data.update({'phone': username})
        else:
            data.update({'username': username})
        payload = self.encrypt_request(data)
        if phone:
            res_data = self.request("POST_UPDATE", phone_action, payload)
            return res_data
        else:
            res_data = self.request("POST_UPDATE", action, payload)
            return res_data

    # 搜索歌曲(1),专辑(10),歌手(100),歌单(1000),用户(1002) *(type)*
    def _search_songs(self, keywords, offset, limit):
        action = uri + '/search/get'
        data = {
            's': keywords,
            'type': 1,
            'offset': offset,
            'total': 'true',
            'limit': limit
        }
        res_data = self.request('POST', action, data)
        try:
            info = {
                'more': offset + limit < res_data['result']['songCount'],
                'next': offset + limit
            }
            return res_data['result']['songs'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_albums(self, keywords, offset, limit):
        action = uri + '/search/get'
        data = {
            's': keywords,
            'type': 10,
            'offset': offset,
            'total': 'true',
            'limit': limit
        }
        res_data = self.request('POST', action, data)
        try:
            info = {
                'more': offset + limit < res_data['result']['albumCount'],
                'next': offset + limit
            }
            return res_data['result']['albums'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_artists(self, keywords, offset, limit):
        action = uri + '/search/get'
        data = {
            's': keywords,
            'type': 100,
            'offset': offset,
            'total': 'true',
            'limit': limit
        }
        res_data = self.request('POST', action, data)
        try:
            info = {
                'more': offset + limit < res_data['result']['artistCount'],
                'next': offset + limit
            }
            return res_data['result']['artists'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_playlists(self, keywords, offset, limit):
        action = uri + '/search/get'
        data = {
            's': keywords,
            'type': 1000,
            'offset': offset,
            'total': 'true',
            'limit': limit
        }
        res_data = self.request('POST', action, data)
        try:
            info = {
                'more': offset + limit < res_data['result']['playlistCount'],
                'next': offset + limit
            }
            return res_data['result']['playlists'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def search(self, keywords, type=1, offset=0, limit=30):
        """get songs list from search keywords"""
        if type == 1:
            return self._search_songs(keywords, offset, limit)
        elif type == 10:
            return self._search_albums(keywords, offset, limit)
        elif type == 100:
            return self._search_artists(keywords, offset, limit)
        elif type == 1000:
            return self._search_playlists(keywords, offset, limit)
        else:
            return [], None

    # 歌曲详情 多组歌曲详情 歌曲地址 歌曲评论 歌曲歌词
    def song_detail(self, song_id):
        action = uri + '/song/detail/?id={}&ids=[{}]'.format(
            song_id, song_id)
        data = self.request('GET', action)
        if data['code'] == 200:
            return data['songs'][0]
        return None

    def songs_detail(self, song_ids):
        action = uri + '/song/detail?ids=[{}]'.format(','.join(map(str,song_ids)))
        res_data = self.request('GET', action)
        if res_data['code'] == 200:
            return res_data['songs']
        return []

    def songs_url(self, song_ids, bitrate=320000):  # 320000(320),192000(192),128000(128)
        action = uri_we + '/song/enhance/player/url'
        data = {
            'ids': song_ids,
            'br': bitrate,
            'csrf_token': self._cookies.get('__csrf')
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return [song['url'] if song['url'] is not None else '' for song in res_data['data']]
        return []

    def song_lyrics(self, song_id):  # tv表示翻译:要翻译(-1),不要(1)
        action = uri + '/song/lyric?id={}&lv=1&kv=1&tv=-1'.format(song_id)
        res_data = self.request('GET', action)
        if res_data['code'] == 200:
            return res_data
        return None

    def song_comments(self, song_id, offset=0, limit=20):
        action = uri_v1 + '/resource/comments/R_SO_4_{}'.format(song_id)
        data = {
            'rid': song_id,
            'offset': offset,
            'total': 'true',
            'limit': limit,
            'csrf_token': self._cookies.get('__csrf')
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data
        return None

    # 专辑描述 专辑详情 专辑评论
    def album_desc(self, album_id):
        action = site_uri + '/album?id={}'.format(album_id)
        res_data = self.request('GET', action)
        if res_data is None:
            return ''
        soup = BeautifulSoup(res_data.content, 'html.parser')
        alb_descs = soup.select('.n-albdesc')
        if alb_descs:
            return alb_descs[0].prettify()
        return ''

    def album_detail(self, album_id):
        action = uri + '/album/{}'.format(album_id)
        res_data = self.request('GET', action)
        if res_data['code'] == 200:
            return res_data['album']
        return None

    def album_comments(self, album_id, offset=0, limit=20):
        action = uri_v1 + '/resource/comments/R_AL_3_{}'.format(album_id)
        data = {
            'rid': album_id,
            'offset': offset,
            'total': 'true',
            'limit': limit,
            'csrf_token': self._cookies.get('__csrf')
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data
        return None

    # 歌手描述 歌手详情 歌手专辑
    def artist_desc(self, artist_id):
        action = site_uri + '/artist/desc?id={}'.format(artist_id)
        res_data = self.request('GET', action)
        if res_data is None:
            return ''
        soup = BeautifulSoup(res_data.content, 'html.parser')
        art_descs = soup.select('.n-artdesc')
        if art_descs:
            return art_descs[0].prettify()
        return ''

    def artist_detail(self, artist_id):  # 只能得到热门歌曲(50首)
        action = uri + '/artist/{}'.format(artist_id)
        res_data = self.request('GET', action)
        try:
            info = {
                'more': False,
                'next': -1
            }
            return res_data, info
        except Exception as e:
            logger.error(str(e))
            return None, None

    def artist_albums(self, artist_id, offset=0, limit=30):
        action = uri + '/artist/albums/{}?offset={}&limit={}'.format(
            artist_id, offset, limit)
        res_data = self.request('GET', action)
        try:
            info = {
                'more': offset + limit < res_data['artist']['albumSize'],
                'next': offset + limit
            }
            return res_data['hotAlbums'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    # 歌单详情 歌单评论
    def playlist_detail(self, playlist_id):
        action = uri + '/playlist/detail?id={}&offset=0&total=true&limit=1001'.format(playlist_id)
        res_data = self.request('GET', action)
        if res_data['code'] == 200:
            return res_data['result']
        return None

    def playlist_comments(self, playlist_id, offset=0, limit=20):
        action = uri_v1 + '/resource/comments/A_PL_0_{}'.format(playlist_id)
        data = {
            'rid': playlist_id,
            'offset': offset,
            'total': 'true',
            'limit': limit,
            'csrf_token': self._cookies.get('__csrf')
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data
        return None

    # 用户详情 用户歌单 用户收藏(专辑 歌手)
    def user_detail(self, user_id):
        action = uri_v1 + '/user/detail/{}'.format(user_id)
        data = {'csrf_token': self._cookies.get('__csrf')}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['profile']
        return None

    def user_playlists(self, user_id, offset=0, limit=30):
        action = uri_we + '/user/playlist'
        data = {
            'uid': user_id,
            'offset': offset,
            'limit': limit
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        try:
            info = {
                'more': res_data['more'],
                'next': offset + limit
            }
            return res_data['playlist'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_albums(self, offset=0, limit=30):
        action = uri_we + '/album/sublist'
        data = {
            'offset': offset,
            'limit': limit,
            'csrf_token': self._cookies.get('__csrf')}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        try:
            info = {
                'more': res_data['hasMore'],
                'next': offset + limit
            }
            return res_data['data'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_artists(self, offset=0, limit=30):
        action = uri_we + '/artist/sublist'
        data = {
            'offset': offset,
            'limit': limit,
            'csrf_token': self._cookies.get('__csrf')}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        try:
            info = {
                'more': res_data['hasMore'],
                'next': offset + limit
            }
            return res_data['data'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    # 私人FM 每日推荐歌曲 每日推荐歌单
    def personal_fm(self):
        action = uri_v1 + '/radio/get'
        data = {'csrf_token': self._cookies.get('__csrf')}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['data']
        return []

    def recommend_songs(self, offset=0, limit=30):
        action = uri_v1 + '/discovery/recommend/songs'
        data = {
            'offset': offset,
            'total': 'true',
            'limit': limit
        }
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['recommend']
        return []

    def recommend_playlists(self):
        action = uri_v1 + '/discovery/recommend/resource'
        data = {'csrf_token': self._cookies.get('__csrf')}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['recommend']
        return []

    # 相似歌曲 相似歌单 相似歌手
    def similar_songs(self, song_id):
        action = uri_v1 + '/discovery/simiSong'
        data = {'songid': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['songs']
        return []

    def similar_playlists(self, song_id):
        action = uri_we + '/discovery/simiPlaylist'
        data = {'songid': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['playlists']
        return []

    def similar_artists(self, artist_id):
        action = uri_we + '/discovery/simiArtist'
        data = {'artistid': artist_id}
        payload = self.encrypt_request(data)
        res_data = self.request('POST', action, payload)
        if res_data['code'] == 200:
            return res_data['artists']
        return []

    # 创建歌单 更新歌单名称 删除歌单
    def new_playlist(self, user_id, name='default'):
        action = uri + '/playlist/create'
        data = {
            'uid': user_id,
            'name': name
        }
        res_data = self.request('POST', action, data)
        if res_data['code'] == 200:
            return res_data['playlist']
        return False

    def update_playlist_name(self, playlist_id, name):
        action = uri + '/playlist/update/name'
        data = {
            'id': playlist_id,
            'name': name
        }
        res_data = self.request('POST', action, data)
        if res_data['code'] == 200:
            return True
        return False

    def delete_playlist(self, playlist_id):
        action = uri + '/playlist/delete'
        data = {
            'id': playlist_id,
            'pid': playlist_id
        }
        res_data = self.request('POST', action, data)
        if res_data['code'] == 200:
            return True
        return False

    # 添加/删除歌单歌曲 收藏/取消收藏歌曲 加入垃圾箱/从垃圾箱中删除
    def update_playlist_song(self, playlist_id, song_id, op):  # op: 'add' or 'del' 如果歌曲已经在列表当中,返回code为502
        action = uri + '/playlist/manipulate/tracks'
        data = {
            'tracks': song_id,  # song id
            'pid': playlist_id,  # playlist id
            'trackIds': '[{}]'.format(song_id),  # song id str
            'op': op  # opation
        }
        res_data = self.request('POST', action, data)
        if res_data['code'] == 200:
            return True
        return False

    def update_favorite_song(self, song_id, op):
        action = uri + '/song/like'
        data = {
            "trackId": song_id,
            "like": 'false' if op == 'del' else 'true',
            "time": 0
        }
        res_data = self.request('POST', action, data)
        if res_data['code'] == 200:
            return True
        return False

    def update_fm_trash(self, song_id, op):
        action = uri + '/radio/trash/{}?alg=RT&songId={}&time={}'.format(
            op, song_id, 0)
        res_data = self.request('GET', action)
        if res_data['code'] == 200:
            return True
        return False

    # 排行榜字典 排行榜 排行榜详情
    top_list_dict = {
        0: ['云音乐飙升榜', '19723756'],
        1: ['云音乐新歌榜', '3779629'],
        2: ['网易原创歌曲榜', '2884035'],
        3: ['云音乐热歌榜', '3778678'],
        4: ['云音乐电音榜', '1978921795'],
        5: ['云音乐嘻哈榜', '991319590'],
        6: ['云音乐ACG音乐榜', '71385702'],
        7: ['云音乐新电力榜', '10520166'],
        8: ['Beatport全球电子舞曲榜', '3812895'],
        9: ['日本Oricon周榜', '60131'],
        10: ['云音乐古典音乐榜', '71384707'],
        11: ['UK排行榜周榜', '180106'],
        12: ['美国Billboard周榜', '60198'],
        13: ['法国 NRJ EuroHot 30周榜', '27135204'],
        14: ['iTunes榜', '11641012'],
        15: ['Hit FM Top榜', '120001'],
        16: ['英国Q杂志中文版周榜', '2023401535'],
        17: ['电竞音乐榜', '2006508653'],
        18: ['KTV嗨榜', '21845217'],
        19: ['台湾Hito排行榜', '112463'],
        20: ['中国TOP排行榜(港台榜)', '112504'],
        21: ['中国TOP排行榜(内地榜)', '64016'],
        22: ['香港电台中文歌曲龙虎榜', '10169002'],
        23: ['中国嘻哈榜', '1899724']
    }

    def return_toplists(self):
        return self.top_list_dict

    def top_songlist(self, bilboard_id):
        action = site_uri + '/discover/toplist?id={}'.format(bilboard_id)
        res_data = self.request('GET', action)
        song_ids = re.findall(r'/song\?id=(\d+)', res_data.text)
        if song_ids == []:
            return []
        return self.songs_detail(song_ids)

    # 精选歌单 精选歌单详情
    def return_playlist_classes(self):
        action = site_uri + '/discover/playlist/'
        res_data = self.request('GET', action)
        classes = []
        playlist_class_dict = {}
        soup = BeautifulSoup(res_data.text, 'html.parser')
        dls = soup.select('dl.f-cb')
        for dl in dls:
            title = dl.dt.text
            sub = [item.text for item in dl.select('a')]
            classes.append(title)
            playlist_class_dict[title] = sub
        return [classes, playlist_class_dict]

    def top_playlists(self, category='全部', order='hot', offset=0, limit=30):
        action = uri + '/playlist/list?cat={}&order={}&offset={}&total={}&limit={}'.format(
            urllib.parse.quote(category), order, offset, 'true' if offset else 'false', limit)
        res_data = self.request('GET', action)
        try:
            info = {
                'more': res_data['more'],
                'next': offset + limit
            }
            return res_data['playlists'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    # 登录加密算法
    def _create_aes_key(self, size):
        return (''.join([hex(b)[2:] for b in os.urandom(size)]))[0:16]

    def _aes_encrypt(self, text, key):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, 2, '0102030405060708')
        enc_text = encryptor.encrypt(text)
        enc_text_encode = base64.b64encode(enc_text)
        return enc_text_encode

    def _rsa_encrypt(self, text):
        e = '010001'
        n = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615' \
            'bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf' \
            '695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46' \
            'bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b' \
            '8e289dc6935b3ece0462db0a22b8e7'
        reverse_text = text[::-1]
        pub_key = RSA.construct([int(n, 16), int(e, 16)])
        encrypt_text = pub_key.encrypt(int(binascii.hexlify(reverse_text), 16),
                                       None)[0]
        return format(encrypt_text, 'x').zfill(256)

    def encrypt_request(self, data):
        text = json.dumps(data)
        first_aes_key = '0CoJUm6Qyw8W8jud'
        second_aes_key = self._create_aes_key(16)
        enc_text = self._aes_encrypt(
            self._aes_encrypt(text, first_aes_key).decode('ascii'),
            second_aes_key).decode('ascii')
        enc_aes_key = self._rsa_encrypt(second_aes_key.encode('ascii'))
        payload = {
            'params': enc_text,
            'encSecKey': enc_aes_key,
        }
        return payload

    # 提供给其他模块(QQ音乐、虾米)调用的外链搜索
    def search_url(self, title, artist_name, duration=0):
        songs, info = self.search(title + artist_name)
        if not songs:
            return ''
        target_song = None
        max_match_ratio = 0.5
        max_duration_difference = 5000
        for song in songs:
            if song['name'].lower() == title.lower():
                ratio = SequenceMatcher(None, song['artists'][0]['name'], artist_name).ratio()
                difference = abs(duration - song['duration']) if duration else 0
                if (ratio > max_match_ratio) and (difference < max_duration_difference):
                    target_song = song
                    if ratio == 1:
                        break
                    max_match_ratio = ratio
        if target_song is not None:
            return self.songs_url('[{}]'.format(target_song['id']))[0]
        else:
            return ''

    # 提供给本模块(网易云)调用的获取外链搜索
    def get_3rd_url(self, title, artist_name, duration):
        try:
            from fuocore.qqmusic.api import api as qqmusic_assister
            target_url = qqmusic_assister.search_url(title, artist_name, duration)
            if target_url is not '':
                return target_url
        except Exception as e:
            logger.error(str(e))
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
        return ''


api = API()
