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
    def get_song(self, identifier):
        """get song by identifier

        :return: song model: :class:`fuocore.models.SongModel`
        """


class LocalProvider(AbstractProvider):
    pass


def register(provider):
    providers.add(provider)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)
