# -*- coding: utf-8 -*-

"""
fuocore.provider
~~~~~~~~~~~~~~~~

provider 意为音乐提供方
"""

from abc import ABC, abstractmethod
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

    @property
    @abstractmethod
    def identifier(self):
        """provider identify"""

    @property
    @abstractmethod
    def name(self):
        """provider name"""
