def show_songs(songs):
    s = ''
    for song in songs:
        s += str(song)
        s += '\t# ' + song.title + ' - ' + \
             ','.join([artist.name for artist in song.artists]) + '\n'
    return s
