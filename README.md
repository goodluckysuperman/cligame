# cligame

一个使用 `uv` 管理的终端文字小说小游戏原型。当前首版提供一个可玩的轻分支短篇《雾钟之夜》，并支持进入结局时展示专属终端图案，同时播放共享结束音效。

## 环境准备

```bash
uv sync
```

## 启动游戏

运行内置故事：

```bash
uv run cligame play
```

指定内置故事：

```bash
uv run cligame play --story first_story
```

从外部 JSON 文件加载故事：

```bash
uv run cligame play --story-file path/to/story.json
```

静音运行：

```bash
uv run cligame play --mute
```

查看内置故事列表：

```bash
uv run cligame list-stories
```

## 开发命令

运行测试：

```bash
uv run pytest
```

运行 lint：

```bash
uv run ruff check .
```

## 结局演出资源

- `src/cligame/content/audio/endings/shared_ending.mp3`：当前所有结局共用的结束音效
- `src/cligame/content/art/endings/`：不同结局对应的终端图案资源

当前行为：
- 到达结局后不会立即退出
- 会显示对应结局图案
- 默认播放共享结束音效
- 按 Enter 后结束本轮游戏

## 项目结构

- `src/cligame/cli.py`：CLI 命令入口
- `src/cligame/game.py`：游戏主循环与结局演出控制
- `src/cligame/story_loader.py`：故事文件加载与校验
- `src/cligame/models.py`：故事数据模型
- `src/cligame/renderer.py`：终端渲染
- `src/cligame/audio.py`：音频接口与 Windows 播放实现
- `src/cligame/content/stories/`：内置可玩故事
- `src/cligame/content/audio/`：运行时音频资源
- `src/cligame/content/art/`：终端图案资源
- `semantic-library.md`：原始语料库，供后续扩写参考
- `docs/prd.md`：第一版需求文档
- `docs/technical-design.md`：第一版技术设计
