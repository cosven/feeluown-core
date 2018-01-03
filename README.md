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

git clone https://github.com/cosven/feeluown-core.git
cd feeluown-core
pip3 install -e .
git clone https://github.com/cosven/feeluown-cli.git
pip3 install -e .
```

## Simple Usage

```
# 启动服务端
fuo --debug

# 另外打开一个 shell
fuocli search '谢春花' | head -n 20
fuocli play fuo://netease/songs/458496082
```
