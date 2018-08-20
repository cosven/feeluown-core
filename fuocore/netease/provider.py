import logging
from contextlib import contextmanager

from fuocore.provider import AbstractProvider
from fuocore.netease.api import API


logger = logging.getLogger(__name__)


class NeteaseProvider(AbstractProvider):
    def __init__(self):
        self.api = API()

        self._user = None

    @property
    def identifier(self):
        return 'netease'

    @property
    def name(self):
        return '网易云音乐'

    @contextmanager
    def auth_as(self, user):
        old_user = self._user
        self.auth(user)
        try:
            yield
        finally:
            self.auth(old_user)

    def auth(self, user):
        assert user.cookies is not None
        self._user = user
        self.api.load_cookies(user.cookies)


provider = NeteaseProvider()


from .models import search  # noqa
provider.search = search
