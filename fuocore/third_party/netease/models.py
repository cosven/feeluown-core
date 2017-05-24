# -*- coding: utf-8 -*-

from april.models import Model

from fuocore.models import BriefSongModel, SongModel


class NBriefSongModel(BriefSongModel):
    id = int

    @property
    def identifier(self):
        return self.id

    @property
    def source(self):
        return 'netease'


class NSongModel(SongModel):
    id = int

    @property
    def identifier(self):
        return self.id

    @property
    def source(self):
        return 'netease'


class NMediaModel(Model):
    id = int
    bitrate = int
    url = str
