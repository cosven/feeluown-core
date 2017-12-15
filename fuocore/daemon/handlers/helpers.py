def show_songs(songs):
    s = ''
    for song in songs:
        s += str(song)
        s += '\t# ' + song.title + ' - ' + \
             ','.join([artist.name for artist in song.artists]) + '\n'
    return s


def show_song(song):
    artists_name = ','.join([artist.name for artist in song.artists])
    if song.album is not None:
        album_name = song.album.name
    else:
        album_name = 'Unknown'
    msgs = (
        'provider     {}'.format(song.source),
        'identifier   {}'.format(song.identifier),
        'title        {}'.format(song.title),
        'artists      {}'.format(artists_name),
        'album        {}'.format(album_name),
        'duration     {}'.format(song.duration),
        'url          {}'.format(song.url),
    )
    return '\n'.join(msgs)
