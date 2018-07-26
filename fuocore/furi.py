# -*- coding: utf-8 -*-

"""
fuocore.furi
~~~~~~~~~~~~

这个模块提供了 furi 相关对象及处理函数。

一个 furi 例子：fuo://local:song:/Music/xxx.mp3
"""

from collections import namedtuple


FUri = namedtuple(
    'FUri',
    ('scheme', 'provider', 'category', 'identifier')
)


def parse_furi(furi):
    scheme, body = furi.split('://')
    provider = category = identifier = None
    if body:
        parts = body.split('/')
        if len(parts) == 3:
            provider, category, identifier = parts
        elif len(parts) == 2:
            provider, category = parts
        else:
            provider = parts[0]

    return FUri(scheme, provider, category, identifier)
