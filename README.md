# feeluown-core (work in progress)

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)

录了个两分钟的简短的演示视频 👇

[![Video Show](http://img.youtube.com/vi/pZyT7mC2-FE/0.jpg)](http://www.youtube.com/watch?v=pZyT7mC2-FE)

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

# use fuocli
fuocli search '谢春花' | grep songs | head -n 10 | awk '{print $1}' | fuocli add
fuocli add fuo://netease/songs/45849608
fuocli remove fuo://netease/songs/45849608
fuocli play fuo://netease/songs/458496082
fuocli list
fuocli status
fuocli pause
fuocli resume
```

## FQA
