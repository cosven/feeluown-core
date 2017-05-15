import json
import random
import sys


sys.path.append('.')

from fuocore.third_party.netease import NeteaseProvider


n_provider = NeteaseProvider()

songs = n_provider.search(u'蔡健雅')
song = random.choice(songs)

print(json.dumps(n_provider.get_song(208889).serialize(), indent=2))
