# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod, abstractproperty


providers = set()


class AbstractProvider(metaclass=ABCMeta):
    """abstract music resource provider"""

    @abstractproperty
    def name(self):
        """provider name, used to identify"""

    @abstractmethod
    def search(self, keyword, **kwargs):
        """search songs by name, artist name, album name

        :return: list of brief songs.
        """

    @abstractmethod
    def list_songs(self, identifier_list):
        """list songs by identifier list

        :return: song model: :class:`fuocore.models.SongModel`
        """

    @abstractmethod
    def get_song(self, identifier):
        """get song by identifier

        :return: song model: :class:`fuocore.models.SongModel`
        """

    def get_lyric(self, identifier):
        return ''

    @abstractmethod
    def get_album(self, identifier):
        """get album by identifier

        :return: album model: :class:`fuocore.models.AlbumModel`
        """


def register(provider):
    providers.add(provider)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)


def get_provider(name):
    for provider in providers:
        if provider.name == name:
            return provider
    return None
