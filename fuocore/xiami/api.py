import json
import logging

import requests


logger = logging.getLogger(__name__)


class Xiami(object):
    '''
    refrence: https://github.com/listen1/listen1
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
        pass

    def song_detail(self, sid):
        pass

    def search(self, keyword):
        search_url = 'http://api.xiami.com/web?v=2.0&app_key=1&key={0}'\
                     '&page=1&limit=50&_ksTS=1459930568781_153&callback=jsonp154'\
                     '&r=search/songs'.format(keyword)
        try:
            res = requests.get(search_url, headers=self._headers)
            json_string = res.content[9:-1]
            data = json.loads(json_string.decode('utf-8'))
            return data['data'].get('songs')
        except Exception as e:
            logger.error(str(e))
        return []
