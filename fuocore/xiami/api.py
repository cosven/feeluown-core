import json
import logging

import requests


logger = logging.getLogger(__name__)


api_base_url = 'http://api.xiami.com/web?v=2.0&app_key=1&r='


class Xiami(object):
    '''
    Why there exists such a weird/strange api?
    '''
    def __init__(self):
        self._headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'api.xiami.com',
            'Referer': 'http://m.xiami.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                          '/33.0.1750.152 Safari/537.36',
        }

    def song_detail(self, sid):
        q = 'song/detail&id={}'.format(sid)
        url = api_base_url + q
        resp = requests.get(url, headers=self._headers)
        song = resp.json()['data']['song']
        # server return an invalid song when song not exists
        if song['song_id'] == 0:
            return None
        return song

    def album_detail(self, bid):
        q = 'album/detail&id={}'.format(bid)
        url = api_base_url + q
        resp = requests.get(url, headers=self._headers)
        album = resp.json()['data']
        if album['album_id'] == 0:
            return None
        return album

    def artist_detail(self, aid):
        q = 'album/detail&id={}'.format(aid)
        url = api_base_url + q
        resp = requests.get(url, headers=self._headers)
        artist = resp.json()['data']
        if artist['artist_id'] == 0:
            return None
        return artist

    def search(self, keyword, page=1, limit=50):
        q = 'search/songs&page={page}&limit={limit}&key={key}'.format(
                key=keyword,
                page=page,
                limit=limit)
        url = api_base_url + q
        res = requests.get(url, headers=self._headers)
        return res['data']['songs']
