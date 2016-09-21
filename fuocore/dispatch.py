# -*- coding: utf-8 -*-

import weakref
from weakref import WeakMethod
import logging


class Signal(object):
    def __init__(self):
        super().__init__()
        self.receivers = set()

    def emit(self, **kwargs):
        for receiver in self.receivers:
            try:
                receiver()(**kwargs)
            except Exception as err:
                logging.exception('receiver %s run error' % receiver())

    def _ref(self, receiver):
        ref = weakref.ref
        if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
            ref = WeakMethod
        return ref(receiver)

    def connect(self, receiver):
        self.receivers.add(self._ref(receiver))

    def disconnect(self, receiver):
        receiver = self._ref(receiver)
        if receiver in self.receivers:
            self.receivers.remove(receiver)
            return True
        return False


def receiver(signal):
    def _decorator(func):
        if isinstance(signal, (list, tuple)):
            for s in signal:
                s.connect(func)
        else:
            signal.connect(func)
        return func
    return _decorator
