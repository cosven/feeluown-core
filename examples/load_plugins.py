# -*- coding: utf-8 -*-

from fuocore import setup_logger
from fuocore.provider import providers
from fuocore.plugin import load_plugins


setup_logger()
load_plugins()


print('检测到下列 provider:')
for provider in providers:
    print(provider)

