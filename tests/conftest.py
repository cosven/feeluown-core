import json

from fuocore.third_party.netease.provider import api


def mock_netease_api_search(*args, **kwargs):
    with open('data/fixtures/search.json') as f:
        data = json.load(f)
        return data['result']['songs']


api.search = mock_netease_api_search
