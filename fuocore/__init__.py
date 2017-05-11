from .player import Player  # noqa
from .provider import providers


__version__ = '0.0.4a'

__all__ = ['Player', 'search']


def search(name=''):

    songs = []
    for provider in providers:
        songs.append(provider.search(name=name))
    return songs
