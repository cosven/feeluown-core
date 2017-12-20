def show_songs(songs):
    s = ''
    for song in songs:
        s += str(song)
        s += '\t# ' + song.title + ' - ' + \
             ','.join([artist.name for artist in song.artists]) + '\n'
    return s


def show_song(song):
    artists_id = ','.join([str(artist.identifier) for artist in song.artists])
    artists_name = ','.join([artist.name for artist in song.artists])
    if song.album is not None:
        album_id = str(song.album.identifier)
        album_name = song.album.name
    else:
        album_id = None
        album_name = 'Unknown'
    msgs = (
        'provider     {}'.format(song.source),
        'identifier   {}'.format(song.identifier),
        'title        {}'.format(song.title),
        'duration     {}'.format(song.duration),
        'url          {}'.format(song.url),
        'artists      {}\t#{}'.format(artists_id, artists_name),
        'album        {}\t#{}'.format(album_id, album_name),
    )
    return '\n'.join(msgs)


def show_artist(artist):
    pass


def show_album(album):
    pass
