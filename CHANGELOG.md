# CHANGELOG

## 2.1a0 (WIP)
- 将 fuocore.protocol 包移动到 feeluown 中
- 删除 fuocore.furi 模块
- 删除 fuocore.main 入口，安装包时不会生成 `feeluown_core_test` 命令

## 2.0.3 (2018-08-26)
- 在 setup.py 中加入 fuocore.xiami 包 by @chen-chao

## 2.0.2 (2018-08-24)
- 加上对虾米音乐的支持 @cyliuu
- protocol 模块小幅重构
- 用 IntEnum 代替 Enum

## 2.0.1 (2018-08-03)
- 给 Library.search 接口加上异常捕获
- 给 QQ 音乐的接口加上超时

## 2.0 (2018-08-02)
- 添加测试和文档
- 清理废弃代码
- 整理无用的接口，避免新开发者混淆

### 2.0a2(WIP)
- 去除 `provider.get_song` 等方法，用 provider.Song.get 代替
    重构之后：provider 和 Model 的关系类似 db 和 Model 的关系
- 添加 QQ 音乐搜索 API
- 废弃之前的 `load_plugin` 逻辑

### 2.0a1
- 给部分 Model 添加 update/delete 方法

### 2.0a0
- no more BriefXxxModel (docs for more detail.)
- remove `current_index` attribute from Playlist
- arguments will be passed to slots when signal emits
- rename MpvPlayer method `quit` to `shutdown`
- add `__eq__` for BaseModel
- add ModelType

## v1.1.0
- 若干 bug 修复

## v1.0.0
- 基本功能健全：播放、搜索、暂停、下一首、加入播放列表等

## v1.0.0a0
- 支持 TCP Server

## v0.0.5a5

- support seek absolute position

## 2016-10-08 v0.0.3a

- refactor Player class, expose `run` interface

## 2016-10-07 v0.0.2b

- player can play next song automaticly
