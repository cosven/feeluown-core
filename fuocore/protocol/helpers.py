"""
fuocore.protocol.handlers.helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

良好的用文字展示一个对象

展示的时候需要注意以下几点：
1. 让 awk、grep 等 shell 工具容易处理

TODO: 让代码长得更好看
"""


def _fit_text(text, length, filling=True):
    """裁剪或者填补字符串，控制其显示的长度

    >>> _fit_text('12345', 6)
    '12345 '
    >>> _fit_text('哈哈哈哈哈s', 6)  # doctest: -ELLIPSIS
    '哈哈 …'
    >>> _fit_text('哈s哈哈哈哈s', 6)  # doctest: -ELLIPSIS
    '哈s哈…'
    >>> _fit_text('sssss', 5)
    'sssss'

    FIXME: 这样可能会截断一些英文词汇
    """
    assert 80 >= length >= 5

    text_len = 0
    len_index_map = {}
    for i, c in enumerate(text):
        # FIXME: 根据目前少量观察，在大部分字体下，
        # \u4e00 后面的字符宽度是英文字符两倍
        if ord(c) < 19968:  # ord(u'\u4e00')
            text_len += 1
            len_index_map[text_len] = i
        else:
            text_len += 2
            len_index_map[text_len] = i

    if text_len <= length:
        if filling:
            return text + (length - text_len) * ' '
        return text

    remain = length - 1
    if remain in len_index_map:
        return text[:(len_index_map[remain] + 1)] + '…'
    else:
        return text[:(len_index_map[remain - 1] + 1)] + ' …'


def show_song(song, uri_length=None, brief=False):
    """以一行文字的方式显示一首歌的信息

    :param uri_length: 控制 song uri 的长度
    :param brief: 是否只显示简要信息
    """
    artists = song.artists or []
    artists_name = ','.join([artist.name for artist in artists])
    title = _fit_text(song.title, 18, filling=False)
    if song.album is not None:
        album_name = song.album.name
        album_uri = str(song.album)
    else:
        album_name = 'Unknown'
        album_uri = ''
    if uri_length is not None:
        song_uri = _fit_text(str(song), uri_length)
    else:
        song_uri = str(song)
    if brief:
        artists_name = _fit_text(artists_name, 20, filling=False)
        s = '{song}\t# {title} - {artists_name}'.format(
            song=song_uri,
            title=title,
            artists_name=artists_name,
            album_name=album_name)
        return s
    artists_uri = ','.join(str(artist) for artist in artists)
    msgs = (
        'provider     {}'.format(song.source),
        '     uri     {}'.format(song_uri),
        '   title     {}'.format(song.title),
        'duration     {}'.format(song.duration),
        '     url     {}'.format(song.url),
        ' artists     {}\t# {}'.format(artists_uri, artists_name),
        '   album     {}\t# {}'.format(album_uri, album_name),
    )
    return '\n'.join(msgs)


def show_songs(songs):
    uri_length = max((len(str(song)) for song in songs)) if songs else None
    return '\n'.join([show_song(song, uri_length=uri_length, brief=True)
                      for song in songs])


def show_artist(artist):
    msgs = [
        'provider      {}'.format(artist.source),
        'identifier    {}'.format(artist.identifier),
        'name          {}'.format(artist.name),
    ]
    if artist.songs:
        songs_header = ['songs::\n']
        songs = ['\t' + each for each in show_songs(artist.songs).split('\n')]
        msgs += songs_header
        msgs += songs
    return '\n'.join(msgs)


def show_album(album, brief=False):
    msgs = [
        'provider      {}'.format(album.source),
        'identifier    {}'.format(album.identifier),
        'name          {}'.format(album.name),
    ]
    if album.artists is not None:
        artists = album.artists
        artists_id = ','.join([str(artist.identifier) for artist in artists])
        artists_name = ','.join([artist.name for artist in artists])
        msgs_artists = ['artists       {}\t#{}'.format(artists_id, artists_name)]
        msgs += msgs_artists
    if not brief:
        msgs_songs_header = ['songs::\n']
        msgs_songs = ['\t' + each for each in show_songs(album.songs).split('\n')]
        msgs += msgs_songs_header
        msgs += msgs_songs
    return '\n'.join(msgs)


def show_playlist(playlist, brief=False):
    if brief:
        content = '{playlist}\t#{name}'.format(
            playlist=playlist,
            name=playlist.name)
    else:
        parts = [
            'name        {}'.format(playlist.name),
            'songs::\n',
        ]
        parts += ['\t' + show_song(song, brief=True) for song in playlist.songs]
        content = '\n'.join(parts)
    return content


def show_user(user):
    parts = [
        'name        {}'.format(user.name),
        'playlists::\n',
    ]
    parts += ['\t' + show_playlist(p, brief=True) for p in user.playlists]
    return '\n'.join(parts)
