# -*- coding: utf-8 -*-


from abc import ABCMeta, abstractclassmethod


providers = set()


class AbstractProvider(ABCMeta):
    """abstract music resource provider"""

    @abstractclassmethod
    def search(cls, name=None, artist=None, album=None, lyrics=None):
        """search songs by name, artist name, album name

        :return: list of brief songs.
        """


def register(provider):
    providers.add(providers)


def deregister(provider):
    if provider in providers:
        providers.remove(provider)
