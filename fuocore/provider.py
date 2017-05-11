# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractclassmethod, abstractproperty


providers = set()


class AbstractProvider(metaclass=ABCMeta):
    """abstract music resource provider"""

    @abstractproperty
    def name(self):
        """provider name"""

    def search(self, name=None, artist=None, album=None, lyrics=None):
        """search songs by name, artist name, album name

        :return: list of brief songs.
        """


def register(provider):
    providers.add(providers)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)
