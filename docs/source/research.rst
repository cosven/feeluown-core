Research
========

fuo language
------------

things need to be done?
1. set volume
2. if current song is 'aaa', next song is 'bbb'


.. code::

   volumn = 100
   add_hook song_changed

It is too hard for me to decide or design a whole new
language, so why not use lisp? A chance to learn lisp and how
to write a parser.

Command
-------
``fuocli -e "volume=1"``

Init file
---------

use -a or -z to specify init file?
''''''''''''''''''''''''''''''''''
tmp do not give user the ability to specify init file.
just use ~/.fuorc as default init file.


怎样较好的抽象不同的资源提供方？
--------------------------------
fuocore 的一个主要目标就是将各个资源进行抽象，统一上层使用各资源的方式。
但各个资源提供方提供的 API 差异较大，功能差别不小，比如网易云音乐
会提供批量接口（根据歌曲 id 批量获取歌曲详情），而虾米和 QQ 音乐就没有
类似接口，这给 fuocore 的实现和设计带来了挑战。

另一方面，就算各音乐平台都提供一样的 API，开发者在开发相关插件的时候，
也不一定会一次性把所有功能都完成，那时，也会存在一个问题：
A 插件有某功能，但是 B 插件没有。

所以，当 B 插件没有该功能的时候，系统内部应该怎样处理？又怎样将该
问题呈现给用户呢？

举个例子，对于网易云音乐来说，它的批量获取歌曲功能可以这样实现::

    NeteaseSongModel.list(song_ids): -> list<SongModel>

但是我们不能给虾米音乐和 QQ 音乐实现这样的功能，那怎么办，
目前有如下方法::

    1. XiamiSongModel.list(song_ids): -> raise NotSupportedError
    2. XiamiSongModel.list -> AttributeError  # 好像不太优雅
