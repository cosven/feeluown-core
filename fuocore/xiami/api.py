import time
import hashlib
import os
import json
import logging
from difflib import SequenceMatcher

import urllib
import requests

logger = logging.getLogger(__name__)

site_url = 'http://www.xiami.com'
api_base_url = 'http://acs.m.xiami.com'


class API(object):
    '''
    Why there exists such a weird/strange api?

    .. warning::

        As xiami do not have batch get songs api, we temporarily
        not using this.
    '''

    def __init__(self):
        super().__init__()
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'acs.m.xiami.com',
            'Referer': 'http://acs.m.xiami.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' XIAMI-MUSIC/3.1.1 Chrome/56.0.2924.87'
                          ' Electron/1.6.11 Safari/537.36'
        }
        self._cookies = dict(header={'appId': 200, 'platformId': 'mac'}, cookie={}, token='')
        self._http = None

    @property
    def cookies(self):
        return self._cookies

    def load_cookies(self, cookies):
        self._cookies.update(cookies)

    def refresh_cookies(self):
        url = api_base_url + '/h5/mtop.alimusic.xuser.facade.xiamiuserservice.login/1.0/'
        self._cookies.update({'cookie': requests.get(url).cookies.get_dict()})
        self._cookies.update({'token': self._cookies['cookie']['_m_h5_tk'].split('_')[0]})

    def set_http(self, http):
        self._http = http

    @property
    def http(self):
        return requests if self._http is None else self._http

    def request(self, method, action, query=None, timeout=3):
        try:
            if method == "GET":
                res = self.http.get(action + query, headers=self._headers,
                                    cookies=self._cookies.get('cookie'), timeout=timeout)
            if res is not None:
                content = res.content
                content_str = content.decode('utf-8')
                content_dict = json.loads(content_str)
                try:
                    return content_dict['data']['data']
                except:
                    return None
            else:
                return None
        except Exception as e:
            logger.error(str(e))
            return None

    # 用户登陆
    def login(self, email, password):
        action = api_base_url + '/h5/mtop.alimusic.xuser.facade.xiamiuserservice.login/1.0/?'
        data = {
            'account': email,
            'password': password
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            self._cookies['header'].update({'accessToken': res_data.get('accessToken')})
        except Exception as e:
            logger.error(str(e))
        return res_data

    # 搜索歌曲(1),专辑(10),歌手(100),歌单(1000)*(type)*
    def _search_songs(self, keywords, page, limit):
        action = api_base_url + '/h5/mtop.alimusic.search.searchservice.searchsongs/1.0/?'
        data = {
            'key': keywords,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': res_data['pagingVO']['page'] < res_data['pagingVO']['pages'],
                'next': page + 1
            }
            return res_data['songs'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_albums(self, keywords, page, limit):
        action = api_base_url + '/h5/mtop.alimusic.search.searchservice.searchalbums/1.0/?'
        data = {
            'key': keywords,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': res_data['pagingVO']['page'] < res_data['pagingVO']['pages'],
                'next': page + 1
            }
            return res_data['albums'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_artists(self, keywords, page, limit):
        action = api_base_url + '/h5/mtop.alimusic.search.searchservice.searchartists/1.0/?'
        data = {
            'key': keywords,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': res_data['pagingVO']['page'] < res_data['pagingVO']['pages'],
                'next': page + 1
            }
            return res_data['artists'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def _search_playlists(self, keywords, page, limit):
        action = api_base_url + '/h5/mtop.alimusic.search.searchservice.searchcollects/1.0/?'
        data = {
            'key': keywords,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': res_data['pagingVO']['page'] < res_data['pagingVO']['pages'],
                'next': page + 1
            }
            return res_data['collects'], info
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

    # 歌曲详情 多组歌曲详情 歌曲评论 歌曲歌词
    def song_detail(self, song_id):
        action = api_base_url + '/h5/mtop.alimusic.music.songservice.getsongdetail/1.0/?'
        data = {'songId': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['songDetail']
        except Exception as e:
            logger.error(str(e))
            return None

    def songs_detail(self, song_ids):
        action = api_base_url + '/h5/mtop.alimusic.music.songservice.getsongs/1.0/?'
        songs = []
        try:
            # FIXME: 这里写个 for 循环应该有点问题
            for start in range(0, len(song_ids), 200):
                data = {'songIds': song_ids[start:min(start + 200, len(song_ids))]}
                payload = self.encrypt_request(data)
                res_data = self.request("GET", action, payload)
                if res_data is None:
                    self.refresh_cookies()
                    payload = self.encrypt_request(data)
                    res_data = self.request("GET", action, payload)
                songs.extend(res_data['songs'])
            return songs
        except Exception as e:
            logger.error(str(e))
            return []

    def songs_url(self, song_files, quality='h'):  # s(740),h(320),l(128),f(64),e(32)
        songs_url = []
        for song_file_list in song_files:
            state = False
            for song_file in song_file_list:
                if song_file['quality'] == quality:
                    if 'listenFile' in song_file:
                        songs_url.append(song_file['listenFile'])
                    else:
                        # 例外情况:song_detail获取到的接口为url字段
                        songs_url.append(song_file['url'])
                    state = True
                    break
            if not state:
                songs_url.append('')
        return songs_url

    def song_lyrics(self, song_id):
        action = api_base_url + '/h5/mtop.alimusic.music.lyricservice.getsonglyrics/1.0/?'
        data = {'songId': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            for lyric in res_data['lyrics']:
                if lyric['type'] == 2:
                    return lyric['content']
            return ''
        except Exception as e:
            logger.error(str(e))
            return ''

    def song_comments(self, song_id):
        action = api_base_url + '/h5/mtop.alimusic.social.commentservice.getcommentlist/1.0/?'
        action_hot = api_base_url + '/h5/mtop.alimusic.social.commentservice.gethotcomments/1.0/?'
        data = {
            'objectId': song_id,
            'objectType': 'song'
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        res_data_hot = self.request("GET", action_hot, payload)
        if res_data_hot is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data_hot = self.request("GET", action_hot, payload)
        comments = {}
        try:
            if 'commentVOList' in res_data:
                comments.update({'List': res_data['commentVOList']})
            if 'hotList' in res_data_hot:
                comments.update({'hotList': res_data_hot['hotList']})
            return comments
        except Exception as e:
            logger.error(str(e))
            return None

    # 专辑详情 专辑评论
    def album_detail(self, album_id):
        action = api_base_url + '/h5/mtop.alimusic.music.albumservice.getalbumdetail/1.0/?'
        data = {'albumId': album_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['albumDetail']
        except Exception as e:
            logger.error(str(e))
            return None

    def album_comments(self, album_id):
        action = api_base_url + '/h5/mtop.alimusic.social.commentservice.getcommentlist/1.0/?'
        action_hot = api_base_url + '/h5/mtop.alimusic.social.commentservice.gethotcomments/1.0/?'
        data = {
            'objectId': album_id,
            'objectType': 'album'
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        res_data_hot = self.request("GET", action_hot, payload)
        if res_data_hot is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data_hot = self.request("GET", action_hot, payload)
        comments = {}
        try:
            if 'commentVOList' in res_data:
                comments.update({'List': res_data['commentVOList']})
            if 'hotList' in res_data_hot:
                comments.update({'hotList': res_data_hot['hotList']})
            return comments
        except Exception as e:
            logger.error(str(e))
            return None

    # 歌手详情 歌手专辑 歌手歌曲 歌手评论
    def artist_detail(self, artist_id):
        action = api_base_url + '/h5/mtop.alimusic.music.artistservice.getartistdetail/1.0/?'
        data = {'artistId': artist_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['artistDetailVO']
        except Exception as e:
            logger.error(str(e))
            return None

    def artist_albums(self, artist_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.music.albumservice.getartistalbums/1.0/?'
        data = {
            'artistId': artist_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['albums'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def artist_songs(self, artist_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.music.songservice.getartistsongs/1.0/?'
        data = {
            'artistId': artist_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['songs'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def artist_comments(self, artist_id):
        action = api_base_url + '/h5/mtop.alimusic.social.commentservice.getcommentlist/1.0/?'
        action_hot = api_base_url + '/h5/mtop.alimusic.social.commentservice.gethotcomments/1.0/?'
        data = {
            'objectId': artist_id,
            'objectType': 'artist'
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        res_data_hot = self.request("GET", action_hot, payload)
        if res_data_hot is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data_hot = self.request("GET", action_hot, payload)
        comments = {}
        try:
            if 'commentVOList' in res_data:
                comments.update({'List': res_data['commentVOList']})
            if 'hotList' in res_data_hot:
                comments.update({'hotList': res_data_hot['hotList']})
            return comments
        except Exception as e:
            logger.error(str(e))
            return None

    # 歌单详情 歌单评论
    def playlist_detail(self, playlist_id):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.getcollectdetail/1.0/?'
        data = {'listId': playlist_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['collectDetail']
        except Exception as e:
            logger.error(str(e))
            return None

    def playlist_comments(self, playlist_id):
        action = api_base_url + '/h5/mtop.alimusic.social.commentservice.getcommentlist/1.0/?'
        action_hot = api_base_url + '/h5/mtop.alimusic.social.commentservice.gethotcomments/1.0/?'
        data = {
            'objectId': playlist_id,
            'objectType': 'collect'
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        res_data_hot = self.request("GET", action_hot, payload)
        if res_data_hot is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data_hot = self.request("GET", action_hot, payload)
        comments = {}
        try:
            if 'commentVOList' in res_data:
                comments.update({'List': res_data['commentVOList']})
            if 'hotList' in res_data_hot:
                comments.update({'hotList': res_data_hot['hotList']})
            return comments
        except Exception as e:
            logger.error(str(e))
            return None

    # 用户详情 用户歌单 用户收藏(歌曲 专辑 歌手 歌单)
    def user_detail(self, user_id):
        action = api_base_url + '/h5/mtop.alimusic.xuser.facade.xiamiuserservice.getuserinfobyuserid/1.0/?'
        data = {'userId': user_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        return res_data

    def user_playlists(self, user_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.getcollectbyuser/1.0?'
        data = {
            'userId': user_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['collects'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_songs(self, user_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.fav.songfavoriteservice.getfavoritesongs/1.0/?'
        data = {
            'userId': user_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['songs'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_albums(self, user_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.fav.albumfavoriteservice.getfavoritealbums/1.0/?'
        data = {
            'userId': user_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['albums'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_artists(self, user_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.fav.artistfavoriteservice.getfavoriteartists/1.0/?'
        data = {
            'userId': user_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['artists'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    def user_favorite_playlists(self, user_id, page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.fav.collectfavoriteservice.getfavoritecollects/1.0/?'
        data = {
            'userId': user_id,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['collects'], info
        except Exception as e:
            logger.error(str(e))
            return [], None

    # 私人FM 每日推荐歌曲 每日推荐歌单
    def personal_fm(self):
        action = api_base_url + '/h5/mtop.alimusic.music.radio.getradiosongs/1.0/?'
        data = {'radioType': 1}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['list']
        except Exception as e:
            logger.error(str(e))
            return []

    def recommend_songs(self):
        action = api_base_url + '/h5/mtop.alimusic.recommend.songservice.getdailysongs/1.0/?'
        data = {}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['songs']
        except Exception as e:
            logger.error(str(e))
            return []

    def recommend_playlists(self):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.getcollects/1.0/?'
        data = {}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['collects']
        except:
            return []

    # 相似歌曲 相似歌单 相似歌手
    def similar_songs(self, song_id):
        # 手机抓到的api(但失效)
        # action = api_base_url + '/h5/mtop.alimusic.music.songservice.getsimilarsongs/1.0/?'
        action = api_base_url + '/h5/mtop.alimusic.music.songservice.getsongext/1.0/?'
        data = {'songId': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['similarSongsFullInfo']
        except Exception as e:
            logger.error(str(e))
            return []

    def similar_playlists(self, song_id):
        # 手机抓到的api(但失效)
        # action = api_base_url + '/h5/mtop.alimusic.music.recommendservice.getrecommendcollects/1.0/?'
        action = api_base_url + '/h5/mtop.alimusic.music.songservice.getsongext/1.0/?'
        data = {'songId': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['collects']
        except Exception as e:
            logger.error(str(e))
            return []

    def similar_artists(self, artist_id):
        action = api_base_url + '/h5/mtop.alimusic.recommend.artistservice.getsimilarartists/1.0/?'
        data = {'artistId': artist_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['artists']
        except Exception as e:
            logger.error(str(e))
            return []

    # 创建歌单 更新歌单名称 删除歌单
    def new_playlist(self, name='default'):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.createcollect/1.0/?'
        data = {'title': name}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        return res_data

    def update_playlist_name(self, playlist_id, name):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.updatecollect/1.0/?'
        data = {
            'listId': playlist_id,
            'title': name
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return True if res_data['success'] == 'true' else False
        except Exception as e:
            logger.error(str(e))
            return None

    def delete_playlist(self, playlist_id):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.deletecollect/1.0/?'
        data = {'listId': playlist_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return True if res_data['success'] == 'true' else False
        except Exception as e:
            logger.error(str(e))
            return None

    # 添加/删除歌单歌曲 收藏/取消收藏歌曲 加入垃圾箱/从垃圾箱中删除(op: 'add' or 'del')
    def update_playlist_song(self, playlist_id, song_id, op):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.{}songs/1.0/?'.format(
            'delete' if op == 'del' else 'add')
        data = {
            'listId': playlist_id,
            'songIds': [song_id]
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return True if res_data['success'] == 'true' else False
        except Exception as e:
            logger.error(str(e))
            return None

    def update_favorite_song(self, song_id, op):
        action = api_base_url + '/h5/mtop.alimusic.fav.songfavoriteservice.{}favoritesong/1.0/?'.format(
            'un' if op == 'del' else '')
        data = {'songId': song_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return True if res_data['status'] == 'true' else False
        except Exception as e:
            logger.error(str(e))
            return None

    def update_fm_trash(self, song_id, op):
        if op == 'add':
            action = api_base_url + '/h5/mtop.alimusic.fav.songfavoriteservice.unlikesong/1.0/?'
            data = {'songId': song_id}
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
            if res_data is None:
                self.refresh_cookies()
                payload = self.encrypt_request(data)
                res_data = self.request("GET", action, payload)
        else:
            # 'GET /ajax/space-unlib-del?song_id=1776252626&_xiamitoken=fd32e81025d027f070729730390c7d63 HTTP/1.1'
            # 暂时曲线救国(先加入喜欢,再取消喜欢)
            self.update_favorite_song(song_id, 'add')
            res_data = self.update_favorite_song(song_id, 'del')
            return res_data
        try:
            return True if res_data['status'] == 'true' else False
        except Exception as e:
            logger.error(str(e))
            return None

    # 排行榜 排行榜详情
    def return_toplists(self):
        action = api_base_url + '/h5/mtop.alimusic.music.billboardservice.getbillboards/1.0/?'
        data = {}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['list']
        except Exception as e:
            logger.error(str(e))
            return []

    def top_songlist(self, billboard_id):
        action = api_base_url + '/h5/mtop.alimusic.music.billboardservice.getbillboarddetail/1.0/?'
        data = {'billboardId': billboard_id}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['billboard']['items']
        except Exception as e:
            logger.error(str(e))
            return []

    # 精选歌单 精选歌单详情(order: 'hot'&'new')
    def return_playlist_classes(self):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.getrecommendtags/1.0/?'
        data = {}
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            return res_data['recommendTags']
        except Exception as e:
            logger.error(str(e))
            return []

    def top_playlists(self, category='', order='hot', page=1, limit=30):
        action = api_base_url + '/h5/mtop.alimusic.music.list.collectservice.getcollects/1.0/?'
        data = {
            'key': category,
            'dataType': order,
            'pagingVO': {
                'page': page,
                'pageSize': limit
            }
        }
        payload = self.encrypt_request(data)
        res_data = self.request("GET", action, payload)
        if res_data is None:
            self.refresh_cookies()
            payload = self.encrypt_request(data)
            res_data = self.request("GET", action, payload)
        try:
            info = {
                'more': True if res_data['more'] == 'true' else False,
                'next': page + 1
            }
            return res_data['collects'], info
        except Exception as e:
            logger.error(str(e))
            return []

    # 地址校验算法
    def _create_sign(self, appkey, t, token, data):
        data = '{}&{}&{}&{}'.format(
            token, t, appkey, data)
        res_data = hashlib.md5(data.encode('utf-8')).hexdigest()
        return res_data

    def encrypt_request(self, model):
        appkey = '12574478'
        t = int(time.time() * 1000)
        token = self._cookies.get('token')
        requestStr = {
            'header': self._cookies.get('header'),
            'model': model
        }
        data = json.dumps({'requestStr': json.dumps(requestStr)})
        sign = self._create_sign(appkey, t, token, data)
        payload = '&t={}&appKey={}&sign={}&data={}'.format(
            t, appkey, sign, urllib.parse.quote(data))
        return payload

    # 提供给其他模块(QQ、网易云)调用的外链搜索
    def search_url(self, title, artist_name, duration=0):
        songs, info = self.search(title + artist_name)
        if not songs:
            return ''
        target_song = None
        max_match_ratio = 0.5
        max_duration_difference = 5000
        for song in songs:
            if song['songName'].lower() == title.lower():
                ratio = SequenceMatcher(None, song['artistName'], artist_name).ratio()
                difference = abs(duration - song['length']) if duration else 0
                if (ratio > max_match_ratio) and (difference < max_duration_difference):
                    target_song = song
                    if ratio == 1:
                        break
                    max_match_ratio = ratio
        if target_song is not None:
            return self.songs_url([target_song['listenFiles']])[0]
        else:
            return ''

    # 提供给本模块(虾米)调用的获取外链搜索
    def get_3rd_url(self, title, artist_name, duration):
        try:
            from fuocore.qqmusic.api import api as qqmusic_assister
            target_url = qqmusic_assister.search_url(title, artist_name, duration)
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
