# feeluown-core (work in progress)

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)


## Install

```sh
sudo apt-get install mpv  # Debian or Ubuntu
brew install mpv  # mac osx

# please always use the latest release
pip3 install 'fuocore>=1.0.0a0'
pip3 install 'fuocli>=0.0.1a0'
```

## Simple Usage

```
# start daemon
fuo --debug

# use netcat
nc  127.0.0.1 23333
# OK feeluown 1.0.0a0
search 周杰伦
# ACK search 周杰伦
# fuo://netease/songs/418603077   #告白气球-周杰伦
# OK
play fuo://netease/songs/418603077
# ACK play fuo://netease/songs/418603077
# OK

# use fuocli
fuocli search '谢春花' | head -n 10 | awk '{print $1}' | fuocli add
fuocli add fuo://netease/songs/45849608
fuocli remove fuo://netease/songs/45849608
fuocli play fuo://netease/songs/458496082
fuocli list
fuocli status
fuocli pause
fuocli resume
```

## FQA
