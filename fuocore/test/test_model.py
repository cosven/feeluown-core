import pytest
import json
import os

from fuocore.models import NSongModel, NAlbumModel, NArtistModel, \
    NPlaylistModel


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
    model = NSongModel.create(song_data)
    assert model.title == 'Sugar'
    assert model.artists_name == 'Maroon 5'
    assert model.length == 235546
    assert model.album_img == 'http://p3.music.126.net/'\
                              'SwbJDnhHO0DUDWvDXJGAfQ==/6655343883051583.jpg'
    assert hasattr(model, 'album_img')
    assert hasattr(model, 'album_name')


def test_album_model(album_data):
    model = NAlbumModel.create(album_data)
    assert model.name == 'Ⅴ'  # \u2164


def test_artsit_model(artist_data):
    model = NArtistModel.create(artist_data)
    assert model.aid == 96266
    assert model.name == 'Maroon 5'


def test_playlist_model(playlist_data, monkeypatch):
    pid = playlist_data['result']['id']
    name = playlist_data['result']['name']
    ptype = playlist_data['result']['specialType']
    uid = playlist_data['result']['userId']
    img_url = playlist_data['result']['coverImgUrl']
    update_time = playlist_data['result']['updateTime']
    desc = playlist_data['result']['description']
    model = NPlaylistModel(pid, name, ptype, uid, img_url, update_time, desc)
    monkeypatch.setattr(model._api, 'playlist_detail', lambda x: playlist_data)
    assert len(model.songs) == 216
