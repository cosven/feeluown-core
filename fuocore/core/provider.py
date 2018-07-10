# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod


class AbstractProvider(ABC):
    """abstract music resource provider"""

    @property
    @abstractmethod
    def identifier(self):
        """provider identify"""

    @property
    @abstractmethod
    def name(self):
        """provider name"""
