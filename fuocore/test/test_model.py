import pytest
import json
import os

from fuocore.models import NSongSchema, NAlbumModel, NArtistModel, \
    NPlaylistSchema


@pytest.fixture
def song_data():
    f_path = os.path.join(os.path.dirname(__file__),
                          'fixtures', 'song.json')
    with open(f_path, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture
def album_data():
    f_path = os.path.join(os.path.dirname(__file__),
                          'fixtures', 'album.json')
    with open(f_path, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture
def artist_data():
    f_path = os.path.join(os.path.dirname(__file__),
                          'fixtures', 'artist.json')
    with open(f_path, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture
def playlist_data():
    f_path = os.path.join(os.path.dirname(__file__),
                          'fixtures', 'playlist.json')
    with open(f_path, 'r') as f:
        data = json.load(f)
    return data


def test_song_model(song_data):
    return
    nsong_schema = NSongSchema()
    result = nsong_schema.load(song_data)
    import pdb
    pdb.set_trace()
    assert model.title == 'Sugar'
    assert model.artists_name == 'Maroon 5'
    assert model.length == 235546
    assert model.album_img == 'http://p3.music.126.net/'\
                              'SwbJDnhHO0DUDWvDXJGAfQ==/6655343883051583.jpg'
    assert hasattr(model, 'album_img')
    assert hasattr(model, 'album_name')

