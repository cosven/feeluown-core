# feeluown-core

[![Documentation Status](https://readthedocs.org/projects/feeluown-core/badge/?version=latest)](http://feeluown-core.readthedocs.org)
[![Build Status](https://travis-ci.org/cosven/feeluown-core.svg?branch=master)](https://travis-ci.org/cosven/feeluown-core)
[![Coverage Status](https://coveralls.io/repos/github/cosven/feeluown-core/badge.svg?branch=master&service=github)](https://coveralls.io/github/cosven/feeluown-core?branch=master)
[![PyPI](https://img.shields.io/pypi/v/fuocore.svg)](https://pypi.python.org/pypi/fuocore)
[![python](https://img.shields.io/pypi/pyversions/fuocore.svg)](https://pypi.python.org/pypi/fuocore)

feeluown-core 是 [feeluown](https://github.com/cosven/FeelUOwn) 的核心模块。

- [👉 详细文档](https://feeluown-core.readthedocs.io)
- [👉 视频演示](https://youtu.be/-JFXo0J5D9E)

### 安装

```sh
sudo apt-get install libmpv1  # Debian or Ubuntu
brew install mpv              # mac osx

pip3 install fuocore --upgrade
pip3 install fuocli --upgrade
```

### 试用

```
# 启动服务
feeluown_core_test

# 使用 fuocli 控制服务
fuocli search '谢春花' | grep songs | head -n 10 | awk '{print $1}' | fuocli add
fuocli add fuo://netease/songs/45849608
fuocli remove fuo://netease/songs/45849608
fuocli play fuo://netease/songs/458496082
fuocli list  # 还有 resume/pause/next/last 等命令

# 在终端查看实时歌词
echo "sub topic.live_lyric" | nc localhost 23334
```
