.. fuocore documentation master file, created by
   sphinx-quickstart on Wed Apr 26 10:49:26 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

feeluown core
=============

mp3 player with multi-source

Usage
-----

搜索歌曲
''''''''

.. sourcecode:: python

    from fuocore import Source
    from fuocore.third_party.netease import NeteaseProvider

    source = Source()
    # source.list_provider()
    netease_provider = NeteaseProvider()
    source.add_provider(netease_provider)
    source.search(u'Luv Letter')

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
