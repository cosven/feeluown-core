import logging
import time

from fuocore.models import SongModel
from fuocore.netease.api import api

logger = logging.getLogger(__name__)


class NSongModel(SongModel):

    def _refresh_url(self):
        self.url = api.weapi_songs_url([int(self.identifier)])[0]['url']

    @property
    def url(self):
        """
        As netease song url will be expired after a period of time,
        we can not use static url here. Currently, we assume that the
        expiration time is 100 seconds, after the url expires, it
        will be automaticly refreshed.
        """
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
