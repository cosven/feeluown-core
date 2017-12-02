"""
fuocore.daemon.handlers.show
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

处理 ``show`` 命令::

    show fuo://               # 列出所有 provider
    show fuo://local/songs    # 显示本地所有歌曲
    show fuo://local/songs/1  # 显示一首歌的详细信息

对于每一个 uri，我们需要给它一个对应的处理函数，而 URI 到处理函数的映射
也就是我们说的 ``路由（route）``。``router`` 管理一组 ``route``，
``The router routes you to a route.``
"""
import re
import os
from urllib.parse import urlparse

from fuocore.furi import parse_furi
from fuocore.daemon.handlers import AbstractHandler
from fuocore.daemon.handlers.helpers import show_songs


class NotFound(Exception):
    pass


class Router(object):
    rules = []
    handlers = {}

    @classmethod
    def register(cls, rule, handler):
        cls.rules.append(rule)

    @classmethod
    def get_handler(cls, rule):
        pass


def _validate_rule(rule):
    """简单的对 rule 进行校验

    TODO: 代码实现需要改进
    """
    if rule:
        if rule == '/':
            return
        parts = rule.split('/')
        if parts.count('') == 1:
            return
    raise ValueError('Invalid rule: {}'.format(rule))


def route(rule):
    """show handler router decorator

    example::

        @route('/<provider_name>/songs')
        def show_songs(provider_name):
            pass
    """
    _validate_rule(rule)
    def decorator(func):
        Router.register(rule, func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        return wrapper
    return decorator


def match(path):
    for rule in Router.rules:
        args_regex = re.compile(r'(<.*?>)')
        match = re.findall(args_regex, rule)
        if not match:
            url_regex_s = rule
        else:
            url_regex_s = re.sub(
                args_regex,
                lambda m: '(?P<{}>[^\/]+)'.format(m.group(0)),
                rule
            )
        url_regex = re.compile(r'^{}$'.format(url_regex_s))
        if url_regex.match(path):
            break


def dispatch(rule, params):
    pass


class ShowHandler(AbstractHandler):

    def handle(self, cmd):
        if cmd.args:
            furi = 'fuo://'
        else:
            furi = cmd.args[0]
        r = urlparse(furi)
        path = os.path.join('/', r.netloc, r.path)
        rule, params = match(path)
        return dispatch(rule, params)

    @route('/')
    def list_providers(self):
        provider_names = (provider.name for provider in
                          self.app.list_providers())
        return '\n'.join(('fuo://' + name for name in provider_names))

    @route('/<provider>/songs')
    def list_songs(self, provider):
        provider = self.app.get_provider(furi.provider)
        return show_songs(provider.songs)
