# cligame

一个使用 `uv` 管理的命令式终端收容游戏原型。当前可玩的内容是第一夜《门限协议》：你必须在 04:00 前，通过查看日志、恢复或隔离模块、保存证据并判断谁在骗你，阻止零号收容室异常同步出去。

## 环境准备

```bash
uv sync
```

## 启动游戏

```bash
uv run cligame play
```

静音运行：

```bash
uv run cligame play --mute
```

查看当前可玩内容：

```bash
uv run cligame list-stories
```

## 核心命令

输入统一使用英文命令。第一夜重点命令：

- `help`
- `status`
- `modules`
- `check task`
- `talk senior`
- `ls <path>`
- `open <path>`
- `relay`
- `reply <target>`
- `scan <module>`
- `restore <module>`
- `isolate <module>`
- `record`
- `history`
- `whoami`
- `inventory`
- `protocols`
- `execute <protocol_key>`

## 音频行为

- 前台阶段会循环播放背景音乐：`src/cligame/content/audio/bgm/background_loop.mp3`
- 进入结局后，背景音乐会停止，并切换为结束音效：`src/cligame/content/audio/endings/shared_ending.mp3`
- `--mute` 会同时关闭背景音乐和结束音效
- 当前真实播放实现优先支持 Windows 环境

## 当前目标体验

第一夜的体验重点是：
- 倒计时压力
- 前辈教学与任务发放
- 恢复模块 = 以风险换信息
- 离线记录器用于识别篡改
- 操作者身份逐步被系统重新定义
- 最终在多个协议之间做决定

## 资源结构

- `src/cligame/content/first_night/files/`：第一夜可读取文件
- `src/cligame/content/audio/bgm/background_loop.mp3`：前台循环背景音乐
- `src/cligame/content/audio/endings/shared_ending.mp3`：结局音效
- `src/cligame/content/art/endings/`：终端结局图案
- `semantic-library.md`：文风与经文素材库
- `剧本内容.md`：高层剧本与产品思路草案

## 开发命令

```bash
uv run pytest
uv run ruff check .
```
