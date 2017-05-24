#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from fuocore.backends import MpvPlayer
from fuocore.source import Source

from fuocore.third_party.netease import NeteaseProvider


player = MpvPlayer()
source = Source()

netease_pvd = NeteaseProvider()
source.add_provider(netease_pvd)

songs = source.search(u'周杰伦')
song = random.choice(songs)
song = netease_pvd.get_song(song.identifier)

player.play(song.url)
player._mpv.wait_for_playback()