# feeluown-core

[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![PyPI](https://img.shields.io/pypi/dm/fuocore.svg)](https://pypi.python.org/pypi/fuocore)

- netease music api with xiami music source as its backup
- a mp3 player (using mpg123 as its backend)

## Install

```sh
sudo apt-get install mpg123  # Debian or Ubuntu
brew install mpg123  # mac osx

pip3 install fuocore
```

## Usage

```
from fuocore import Player

player = Player()
player.play_song('url')
```
