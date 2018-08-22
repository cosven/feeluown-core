fuocore 架构设计
================

fuocore 是 feeluown core 的缩写，它是 feeluown 的核心模块。
而 fuocore 又由几个小模块组成，它们分别是：

1. ``音乐库模块`` ：对各平台音乐资源进行抽象及统一
2. ``fuo 协议模块`` ：让音乐资源以 text 的形式呈现，定义了一些控制指令和语法
3. ``播放器模块`` ：音乐播放器
4. ``歌词模块`` ：歌词解析

另外，为了实现一些功能，fuocore 也实现了几个基础组件

1. asyncio/threading tcp server
2. signal/slot
3. pubsub server

.. note::

   Q: 为什么部分基础组建已经有更好的开源实现，为什么我们这里重新造了一个轮子？
   比如 tcp server，Python 标准库 Lib/socketserver.py 中提供了更加完善的
   TcpServer 实现。

   A: 我也不知道为啥，大概是为了学习和玩耍，嘿嘿～ 欢迎大家对它们进行改造。


音乐库模块
----------

音乐库模块是 fuocore 的核心模块，其它各模块都是基于该模块的。
音乐库模块定义了音乐相关的一些领域模型。比如歌曲模型、歌手模型、专辑模型等。
这些模型在代码中的体现就是一个个 Model，这些 Model 都定义在 models.py 中，
举个例子，我们对歌曲模型的定义为::

    class SongModel(BaseModel):
        class Meta:
            model_type = ModelType.song.value
            # TODO: 支持低/中/高不同质量的音乐文件
            fields = ['album', 'artists', 'lyric', 'comments', 'title', 'url',
                      'duration', ]

        @property
        def artists_name(self):
            return ','.join((artist.name for artist in self.artists))

        @property
        def album_name(self):
            return self.album.name if self.album is not None else ''

        @property
        def filename(self):
            return '{} - {}.mp3'.format(self.title, self.artists_name)

        def __str__(self):
            return 'fuo://{}/songs/{}'.format(self.source, self.identifier)  # noqa

        def __eq__(self, other):
            return all([other.source == self.source,
                        other.identifier == self.identifier])

这个模型的核心意义在于：它定义了一首歌曲 **有且只有** 某些属性， **其它模块可以依赖这些属性** 。
举个例子，在程序的其它模块中，当我们遇到 song 对象时，我们可以确定，
这个对象一定会有 title 属性。
