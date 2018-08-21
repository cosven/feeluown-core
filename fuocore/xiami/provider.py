import logging

from contextlib import contextmanager
from fuocore.provider import AbstractProvider
from fuocore.xiami.api import API


logger = logging.getLogger(__name__)


class XiamiProvider(AbstractProvider):
    def __init__(self):
        self.api = API()

        self._user = None

    @property
    def identifier(self):
        return 'xiami'

    @property
    def name(self):
        return '虾米音乐'

    @contextmanager
    def auth_as(self, user):
        # TODO
        old_user = self._user
        self.auth(user)
        try:
            yield
        finally:
            self.auth(old_user)

    def auth(self, user):
        # TODO
        assert user.access_token is not None
        self._user = user
        self.api.set_access_token(user.access_token)


provider = XiamiProvider()


# 让 provider 能够发现对应 Model
from .models import search  # noqa

provider.search = search
