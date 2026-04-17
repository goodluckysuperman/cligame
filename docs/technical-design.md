# Technical Design：cligame 第一版

## 1. 架构概览

项目采用 `src` 布局，把 CLI、故事引擎、渲染、数据模型和内容资源分开，避免首版逻辑继续堆在单文件入口中。

## 2. 模块职责

### `src/cligame/cli.py`
- 解析 CLI 参数。
- 分发 `play` 和 `list-stories` 命令。
- 负责选择内置故事或外部故事文件。

### `src/cligame/game.py`
- 驱动主游戏循环。
- 负责节点切换、读取用户输入。
- 在到达结局时切换到专用结局演出页，而不是立刻退出。

### `src/cligame/models.py`
- 定义 `Story`、`StoryNode`、`Choice`。
- 结局节点支持 `ending_art` 元数据。

### `src/cligame/story_loader.py`
- 从 JSON 载入故事。
- 校验节点、起点、跳转目标是否合法。
- 枚举内置故事。

### `src/cligame/renderer.py`
- 使用 `rich` 渲染标题、正文、选项和结局页。
- 负责从文本资源加载终端图案并展示。

### `src/cligame/audio.py`
- 提供音频接口抽象。
- 默认保留 `NoopAudioPlayer`。
- 在 Windows 下提供共享结束音效的播放实现。

## 3. 内容组织

### 内置故事

内置故事位于 `src/cligame/content/stories/`，每个故事使用一个 JSON 文件。

当前首个故事：
- `src/cligame/content/stories/first_story.json`

### 语料库

- 根目录 `semantic-library.md`：原始创作语料。
- `src/cligame/content/corpus/semantic-library.md`：包内参考说明。

### 音频与图案资源

- `src/cligame/content/audio/endings/shared_ending.mp3`：当前所有结局共用的结束音效
- `src/cligame/content/art/endings/*.txt`：结局图案资源

原则：
- 语料负责提供风格和句式灵感。
- 可玩故事必须使用结构化 JSON 单独维护。
- 终端图案与音频作为独立资源文件维护，不直接硬编码到故事文本中。

## 4. 故事 JSON 格式

```json
{
  "id": "first_story",
  "title": "故事标题",
  "intro": "序章文本",
  "start_node": "opening",
  "nodes": [
    {
      "id": "opening",
      "text": "场景文本",
      "choices": [
        { "label": "选择一", "next": "node_a", "tag": "branch_a" }
      ]
    },
    {
      "id": "ending_a",
      "text": "结局前文本",
      "ending_title": "结局名称",
      "ending_art": "ending_a",
      "ending": "结局正文"
    }
  ]
}
```

约束：
- 非结局节点必须有 `choices`。
- 结局节点不能再定义 `choices`。
- `start_node` 和所有 `next` 必须能在节点表中找到。

## 5. CLI 设计

### 命令

- `uv run cligame play`
- `uv run cligame play --story first_story`
- `uv run cligame play --story-file <path>`
- `uv run cligame play --mute`
- `uv run cligame list-stories`

### 结局行为

到达结局后：
- 渲染结局图案
- 渲染结局文本
- 默认播放共享结束音效
- 等待用户按 Enter 后退出

## 6. 测试策略

### `tests/test_story_loader.py`
- 校验内置故事可枚举。
- 校验内置故事可成功加载。
- 校验结局图案键被正确读取。
- 校验非法跳转会触发错误。

### `tests/test_game_flow.py`
- 模拟输入。
- 覆盖非法输入重试。
- 覆盖一条完整通关路径。
- 确认结束页提示存在。
- 确认会话结束后音频状态被清理。

## 7. 后续扩展方向

- 为不同结局配置不同音频，而不再共用单一结束音效。
- 接入更稳定的跨平台音频播放层。
- 为故事增加元数据与章节机制。
- 增加存档、回看、快速重开。
- 支持从语料模板半自动生成故事草稿。
