import asyncio

from fuocore.daemon import run
from fuocore.local.provider import LocalProvider
from fuocore.player import MpvPlayer
from fuocore.provider import providers, register
from fuocore.source import Source


class App(object):
    def __init__(self):
        self.player = MpvPlayer()
        self.source = Source()

    def list_providers(self):
        for provider in providers:
            yield provider

    def get_provider(self, name):
        for provider in providers:
            if provider.name == name:
                return provider
        return None

    def play(self, song_identifier):
        song = self.source.get_song(song_identifier)
        self.player.play_song(song)


def main():
    app = App()
    app.player.initialize()
    local_provider = LocalProvider()
    register(local_provider)
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run(app))
    event_loop.run_forever()


if __name__ == '__main__':
    main()
