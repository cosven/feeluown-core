# CHANGELOG

## 2.3a1 (WIP)
- 修复 QQ 音乐时间显示问题
- 当一个字段属于 `fields_no_get` 并且值为 None 时，
  `Model.__getattribute__` 中调用 get 时，不覆盖
- 本地音乐 identifier 计算：去掉连接符，增大不同歌曲 `identifier_str` 的区别度
- 修复：正确处理 QQ 音乐没有歌曲的专辑

## 2.3a0 (2018-12-29)
- Model 支持 `create_by_display` 工厂函数
  - 给 BaseModel 添加 `__getattribute__` 方法
  - 给 NBaseModel 和 XBaseModel 移除 `__getattribute__` 方法和
    `_detail_fields` 类属性
- QQ 音乐 SongModel 支持 get 方法

## 2.2 (2018-12-28)
- 发一个 2.2 的正式版（经过测试，相对稳定）

## 2.2b1 (2018-12-02)
- QQ 音乐支持显示歌手和专辑详情
- 设计变化：
  - 支持将 source 做为 Model 的类属性

## 2.2a2 (2018-11-07)
- 修复 Player 若干小问题

## 2.2a1 (2018-11-07)

- 播放器相关 API 修改

  1. 单曲循环时，`playlist.next_song` 返回的歌曲是下一首，
     而不是当前歌曲；之前是返回当前歌曲。
  2. 单曲循环时，`player.play_next` 方法会切换到下一首；
     之前是播放当前歌曲。
  3. `playlist.add` 总是把歌曲添加到播放列表末尾；以前是插入到当前歌曲后面。
  4. 删除 player playlist setter，目前不支持用户设置 playlist

## 2.2a0 (2018-11-06)
- 给 library 添加 `list_song_standby` 接口
- **BREAKING CHANGE**: 修改本地音乐 ID 计算方法
## 2.1 (2018-10-08)
- 修复 XUserModel 的问题
- 完善接口文档

## 2.1a1 (2018-9-18)
- 修复不能使用随机播放模式的问题

## 2.1a0 (2018-9-10)
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
