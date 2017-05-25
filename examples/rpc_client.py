#!/usr/bin/env python3

import asyncio
from pprint import pprint

from aiozmq import rpc


@asyncio.coroutine
def test():
    client = yield from rpc.connect_rpc(connect='tcp://127.0.0.1:7777')
    song = yield from client.call.current_song()
    pprint(song)


event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(test())
