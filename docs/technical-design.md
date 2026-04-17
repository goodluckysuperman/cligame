# Technical Design：Threshold Protocol / 门限协议

## 1. 架构概览

项目从分支小说模型升级为“终端会话状态机”。核心不再是节点跳转，而是：
- GameState
- 命令分发
- 模块状态变化
- 文件解锁与文本污染
- 协议执行
- 前台背景音乐与结局音频切换

## 2. 核心模块

### `src/cligame/cli.py`
负责启动第一夜会话、处理 `play` 和 `list-stories` 命令，并在前台阶段启动循环背景音乐。

### `src/cligame/game.py`
包含 `FirstNightEngine`：
- 保存 `GameState`
- 解析命令
- 推进时间
- 修改模块状态
- 管理任务阶段
- 检查协议可用性

### `src/cligame/models.py`
定义：
- `ModuleStatus`
- `ModuleDefinition`
- `TaskDefinition`
- `ProtocolDefinition`
- `RelayMessage`
- `GameState`

### `src/cligame/renderer.py`
负责：
- 开机 HUD
- 输出命令结果
- 提示当前任务与常用命令
- 显示结局图案与结局文本

### `src/cligame/audio.py`
提供统一音频抽象：
- `start_bgm()` 用于前台循环背景音乐
- `play_ending()` 用于结局音效
- `stop_bgm()` 用于清理当前播放进程

在 Windows 下使用 PowerShell + `System.Windows.Media.MediaPlayer` 实现实际播放。

## 3. 第一夜内容组织

### `src/cligame/first_night_data.py`
集中定义：
- 模块
- 任务
- 协议
- 前辈消息
- 远程消息

### `src/cligame/content/first_night/files/`
存放首批可读文件：
- archive
- audio
- camera
- auth
- protocols

### `src/cligame/content/audio/`
- `bgm/background_loop.mp3`：前台循环背景音乐
- `endings/shared_ending.mp3`：当前所有结局共用的结束音效

## 4. 音频策略

### 前台阶段
- 在 CLI 主循环开始前启动 `background_loop.mp3`
- 使用循环播放逻辑保持 BGM 持续存在

### 结局阶段
- 停止 BGM
- 切换为 `shared_ending.mp3`
- 结局页结束后统一 stop

### 静音模式
- `--mute` 同时关闭 BGM 与 ending 音效

## 5. 玩法循环

第一夜玩法循环：
1. 开场事故面板
2. 前辈接入并教学
3. 玩家执行调查命令
4. 玩家决定信任方向
5. 玩家恢复或隔离模块
6. 信息与身份开始变化
7. 协议逐步开放
8. 玩家执行最终协议
9. 显示结局页与结束音效

## 6. 动态变化设计

### 时间变化
核心命令会消耗时间。

### 模块变化
恢复/隔离模块改变世界状态、文件可见性、异常完整度和身份绑定。

### 文本变化
部分文件会根据玩家的历史行为返回不同文本，例如恢复 audio 后，日志内容改变。

### 身份变化
`whoami` 会随着行为变化而改变：
- 未认证
- 绑定进行中
- 门限适配通过

## 7. 协议执行

首版协议：
- minimum_lockdown
- identity_cutoff
- forced_purge
- threshold_reset

协议是否可执行由前置条件决定，而不是默认全部开放。

## 8. 测试重点

- 命令是否推动任务阶段
- 模块恢复是否改变文件内容
- 协议是否能在满足条件后开放
- CLI 入口与 `list-stories` 是否仍可用
- 静音模式下流程仍可正常结束
