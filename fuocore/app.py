import logging

from fuocore import MpvPlayer, Source, providers

from .plugin import load_plugins


logger = logging.getLogger(__name__)


class App(object):
    def __init__(self):
        self.player = MpvPlayer()
        self.playlist = self.player.playlist
        self.source = Source()

    def initialize(self):
        self.player.initialize()
        load_plugins()

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
        if song is not None:
            self.player.play_song(song)
