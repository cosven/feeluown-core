# -*- coding: utf-8 -*-

import logging
import pkg_resources

from fuocore.provider import AbstractProvider


logger = logging.getLogger(__name__)


def load_providers():
    """load all installed plugins"""
    providers = []

    # load available providers
    for entry_point in pkg_resources.iter_entry_points('fuo.provider'):
        logger.info('Loading provider from plugins: %s', entry_point)
        try:
            provider_cls = entry_point.load(require=False)
        except Exception as e:
            logger.exception("Failed to load plugin %s: %s" % (
                entry_point.name, e))
            continue

        try:
            if not issubclass(provider_cls, AbstractProvider):
                raise TypeError  # issubclass raises TypeError on non-class
        except TypeError:
            logger.error('%s: is invalid plugin.', entry_point.name)
            continue

        try:
            provider = provider_cls()
        except Exception:
            logger.exception('init provider failed')
            continue
        providers.append(provider)
    return providers
