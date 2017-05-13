import json

from fuocore.third_party.netease.provider import api


def mock_netease_api_search(*args, **kwargs):
    with open('data/fixtures/search.json') as f:
        data = json.load(f)
        return data['result']['songs']


def mock_netease_api_weapi_songs_url(*args, **kwargs):
    with open('data/fixtures/media.json') as f:
        return json.load(f)


def mock_netease_api_song_detail(*args, **kwargs):
    with open('data/fixtures/song.json') as f:
        return json.load(f)['songs'][0]


api.search = mock_netease_api_search
api.weapi_songs_url = mock_netease_api_weapi_songs_url
api.song_detail = mock_netease_api_song_detail
