"""
fuocore.daemon.handlers.helper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

良好的用文字展示一个对象

展示的时候需要注意以下几点：
1. 让 awk、grep 等 shell 工具容易处理

TODO: 让代码长得更好看
"""


def show_song(song, brief=False):
    artists = song.artists or []
    artists_name = ','.join([artist.name for artist in artists])
    if song.album is not None:
        album_name = song.album.name
        album_uri = str(song.album)
    else:
        album_name = 'Unknown'
        album_uri = ''
    if brief:
        s = '{song}\t#{title}-{artists_name}-{album_name}'.format(
            song=song,
            title=song.title,
            artists_name=artists_name,
            album_name=album_name)
        return s
    artists_uri = ','.join(str(artist) for artist in artists)
    msgs = (
        'provider     {}'.format(song.source),
        'uri          {}'.format(str(song)),
        'title        {}'.format(song.title),
        'duration     {}'.format(song.duration),
        'url          {}'.format(song.url),
        'artists      {}\t#{}'.format(artists_uri, artists_name),
        'album        {}\t#{}'.format(album_uri, album_name),
    )
    return '\n'.join(msgs)


def show_songs(songs):
    return '\n'.join([show_song(song, brief=True) for song in songs])


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
