#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from fuocore.backends import MpvPlayer
from fuocore.source import Source

from fuocore.third_party.netease import NeteaseProvider


player = MpvPlayer()
player.initialize()
source = Source()

netease_pvd = NeteaseProvider()
source.add_provider(netease_pvd)

songs = source.search(u'周杰伦')
song1 = random.choice(songs[:10])
song1 = netease_pvd.get_song(song1.identifier)
song2 = random.choice(songs[:10])
song2 = netease_pvd.get_song(song2.identifier)

player.playlist.add(song1)
player.play_song(song2)
import time
time.sleep(2)
player._mpv.seek(240)
player._mpv.wait_for_playback()
