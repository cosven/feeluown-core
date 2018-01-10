#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random

from fuocore.player import MpvPlayer
from fuocore.source import Source
from fuocore.local.provider import LocalProvider
from fuocore.netease.provider import NeteaseProvider


player = MpvPlayer()
source = Source()

netease_pvd = NeteaseProvider()
local_pvd = LocalProvider()
source.add_provider(netease_pvd)

# songs = source.search(u'周杰伦')
songs = local_pvd.search(u'张震岳')
song = random.choice(songs)
# song = netease_pvd.get_song(song.identifier)

player.play(song.url)
player._mpv.wait_for_playback()
