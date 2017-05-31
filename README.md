# feeluown-core

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)


- netease/xiami music api as its `source` `provider`
- `player` with replacable `backends`. Note: mpv is the default backend

## Install

```sh
sudo apt-get install mpv  # Debian or Ubuntu
brew install mpv  # mac osx

pip3 install fuocore
```

## Usage

```python
>>> from fuocore.backends import MpvPlayer

>>> player = MpvPlayer()
>>> player.play('data/test_music/one_tree.mp3')
```
