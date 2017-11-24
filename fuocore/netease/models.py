import logging
import time

from fuocore.models import SongModel
from fuocore.netease.api import api

logger = logging.getLogger(__name__)


class NSongModel(SongModel):

    @property
    def url(self):
        if hasattr(self, '_expired_at'):
            if time.time() > self._expired_at:
                logger.debug('song({}) url is expired, refresh...'
                             .format(self))
                self.url = api.weapi_songs_url(
                    [int(self.identifier)])[0]['url']
            return self._url
        raise RuntimeError('song url should not be None')

    @url.setter
    def url(self, value):
        self._expired_at = time.time() + 10
        self._url = value
