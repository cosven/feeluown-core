Introduction
============

Have you ever heard `Music Player Daemon`_? Conceptually,
fuocore(feeluown core) is also a MPD, but fuocore has its own
protocol and architecture which are totally different from the
normal MPD.

* It defines its own text control protocol on top of tcp.
  Users send text as input to ask fuocore do something and
  fuocore output a text message as response, which can be easily
  processed with unix shell tools such as grep, awk, etc.
  See :doc:`./protocol` for more details.

* It construct a abstract music library by using xiami, qq, netease
  and local music as its resource :term:`provider`. For example,
  when we do a search operation, fuocore will launch search
  request to each provider, and then do ordering and filtering
  on search results. Fuocore identify every resource
  (song, artist, album, etc.) by giving them a uri like
  'fuo://provider/songs/identifier'.

* By default, it use `MPV`_ as player backend.



.. _Music Player Daemon: https://musicpd.org/
.. _MPV: https://mpv.io/
