# feeluown-core

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master&service=github)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)

feeluown-core 是一个可扩展性强，功能齐全的音乐播放服务器。

几个主要特性：

1. 基于 text 的通信协议，能和 Emacs/tmux 等工具良好集成
   [protocol](http://feeluown-core.readthedocs.io/en/latest/protocol.html#fuo-protocol)，
2. 在 dotfile 中管理自己喜欢的音乐
   [for example](https://github.com/cosven/cosven.github.io/blob/master/music/mix.fuo)
3. 支持从 netease/xiami 获取免费的音乐资源

录了个几分钟的简短的演示视频 👇

[![Video Show](http://img.youtube.com/vi/-JFXo0J5D9E/0.jpg)](https://youtu.be/-JFXo0J5D9E)

## Install

```sh
sudo apt-get install libmpv1  # Debian or Ubuntu
brew install mpv  # mac osx

# please always use the latest release
pip3 install fuocore --upgrade
pip3 install fuocli --upgrade
```

## Simple Usage

```
# start daemon
fuo
# nohup fuo &  # 后台运行

# use fuocli
fuocli search '谢春花' | grep songs | head -n 10 | awk '{print $1}' | fuocli add
fuocli add fuo://netease/songs/45849608
fuocli remove fuo://netease/songs/45849608
fuocli play fuo://netease/songs/458496082
fuocli list
fuocli next
fuocli status
fuocli pause
fuocli resume
```

## FQA

## Contributing to fuocore
请参考文档 [Development](http://feeluown-core.readthedocs.io/en/latest/development.html)
