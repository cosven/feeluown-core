import logging
import time
import os

from fuocore.consts import MUSIC_LIBRARY_PATH
from fuocore.models import SongModel
from fuocore.netease.api import api

logger = logging.getLogger(__name__)


class NSongModel(SongModel):

    def _refresh_url(self):
        songs = api.weapi_songs_url([int(self.identifier)])
        if songs:
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
        self._expired_at = time.time() + 100
        self._url = value
