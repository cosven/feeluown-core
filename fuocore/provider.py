# -*- coding: utf-8 -*-

"""
fuocore.provider
~~~~~~~~~~~~~~~~

"""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from fuocore.models import (
    SongModel,
    ArtistModel,
    AlbumModel,
    PlaylistModel,
    LyricModel,

    UserModel,
)


class AbstractProvider(ABC):
    """abstract music resource provider
    """

    # A well behaved provider should implement its own models .
    Song = SongModel
    Artist = ArtistModel
    Album = AlbumModel
    Playlist = PlaylistModel
    Lyric = LyricModel
    User = UserModel

    def __init__(self):
        self._user = None

    @property
    @abstractmethod
    def identifier(self):
        """provider identify"""

    @property
    @abstractmethod
    def name(self):
        """provider name"""

    @contextmanager
    def auth_as(self, user):
        """auth as a user temporarily"""
        old_user = self._user
        self.auth(user)
        try:
            yield
        finally:
            self.auth(old_user)

    @abstractmethod
    def auth(self, user):
        """use provider as a specific user"""
