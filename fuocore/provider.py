# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractmethod, abstractproperty


providers = set()


class AbstractProvider(metaclass=ABCMeta):
    """abstract music resource provider"""

    @abstractproperty
    def name(self):
        """provider name"""

    @abstractmethod
    def search(self, name=None, artist=None, album=None, lyrics=None):
        """search songs by name, artist name, album name

        :return: list of brief songs.
        """


class LocalProvider(AbstractProvider):
    pass


def register(provider):
    providers.add(provider)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)
