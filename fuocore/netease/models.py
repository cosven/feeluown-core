import logging
import time
import os

from fuocore.consts import MUSIC_LIBRARY_PATH
from fuocore.models import (
    BaseModel,
    SongModel,
    LyricModel,
    PlaylistModel,
    AlbumModel,
    ArtistModel,
)
from fuocore.netease.api import api


logger = logging.getLogger(__name__)


class NBaseModel(BaseModel):
    detail_fields = ()

    @classmethod
    def get(cls, identifier):
        raise NotImplementedError

    def __getattribute__(self, name):
        cls = type(self)
        value = object.__getattribute__(self, name)
        if name in cls.detail_fields and not value:
            obj = cls.get(self.identifier)
            self = obj
            value = object.__getattribute__(self, name)
        return value


class NSongModel(SongModel, NBaseModel):
    @classmethod
    def get(cls, identifier):
        data = api.song_detail(int(identifier))
        song, _ = NeteaseSongSchema(strict=True).load(data)
        return song

    def _refresh_url(self):
        songs = api.weapi_songs_url([int(self.identifier)])
        if songs and songs[0]['url']:
            self.url = songs[0]['url']
        else:
            self.url = self._find_in_xiami()

    def _find_in_xiami(self):
        logger.debug('try to find {} equivalent in xiami'.format(self))
        return api.get_xiami_song(
            title=self.title,
            artist_name=self.artists_name
        )

    def _find_in_local(self):
        path = os.path.join(MUSIC_LIBRARY_PATH, self.filename)
        if os.path.exists(path):
            logger.debug('find local file for {}'.format(self))
            return path
        return None

    # NOTE: if we want to override mode attribute, we must
    # implement both getter and setter.
    @property
    def url(self):
        """
        We will always check if this song file exists in local library,
        if true, we return the url of the local file.
        If a song does not exists in netease library, we will *try* to
        find a equivalent in xiami temporarily.

        .. note::

            As netease song url will be expired after a period of time,
            we can not use static url here. Currently, we assume that the
            expiration time is 100 seconds, after the url expires, it
            will be automaticly refreshed.
        """
        local_path = self._find_in_local()
        if local_path:
            return local_path

        if not self._url:
            self._refresh_url()
        elif hasattr(self, '_expired_at'):
            if time.time() > self._expired_at:
                logger.debug('song({}) url is expired, refresh...'
                             .format(self))
                self._refresh_url()
        else:
            raise RuntimeError('song url should not be None')
        return self._url

    @url.setter
    def url(self, value):
        self._expired_at = time.time() + 60 * 60 * 1  # one hour
        self._url = value

    @property
    def lyric(self):
        if self._lyric is not None:
            assert isinstance(self._lyric, LyricModel)
            return self._lyric
        data = api.get_lyric_by_songid(self.identifier)
        lrc = data.get('lrc', {})
        lyric = lrc.get('lyric', '')
        self._lyric = LyricModel(
            identifier=self.identifier,
            source=self.source,
            content=lyric
        )
        return self._lyric

    @lyric.setter
    def lyric(self, value):
        self._lyric = value


class NAlbumModel(AlbumModel, NBaseModel):
    detail_fields = ('cover', 'songs', 'artists', )

    @classmethod
    def get(cls, identifier):
        album_data = api.album_infos(identifier)
        if album_data is None:
            return None
        album, _ = NeteaseAlbumSchema(strict=True).load(album_data)
        return album


class NArtistModel(ArtistModel, NBaseModel):
    detail_fields = ('songs', 'cover')

    @classmethod
    def get(cls, identifier):
        artist_data = api.artist_infos(identifier)
        artist = artist_data['artist']
        artist['songs'] = artist_data['hotSongs']
        artist, _ = NeteaseArtistSchema(strict=True).load(artist)
        return artist


class NPlaylistModel(PlaylistModel, NBaseModel):
    detail_fields = ('songs', )

    @classmethod
    def get(cls, identifier):
        data = api.playlist_detail(identifier)
        playlist, _ = NeteasePlaylistSchema(strict=True).load(data)
        return playlist


# import loop
from .schemas import (
    NeteaseSongSchema,
    NeteaseAlbumSchema,
    NeteaseArtistSchema,
    NeteasePlaylistSchema,
)
