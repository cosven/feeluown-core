#!/usr/bin/env python3

from fuocore.provider import LocalProvider


lp = LocalProvider()
songs = lp.search('张震岳')
for song in songs:
    print(song)
