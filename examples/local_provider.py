#!/usr/bin/env python3

from fuocore import setup_logger
from fuocore.local.provider import LocalProvider

setup_logger()

lp = LocalProvider()
songs = lp.search('张震岳')
for song in songs:
    print(song)
