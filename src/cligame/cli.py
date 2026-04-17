from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from .audio import create_audio_player
from .game import GameSession
from .renderer import StoryRenderer
from .story_loader import list_builtin_stories, load_builtin_story, load_story_from_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cligame", description="终端文字小说小游戏")
    subparsers = parser.add_subparsers(dest="command", required=True)

    play_parser = subparsers.add_parser("play", help="开始游戏")
    play_parser.add_argument("--story", default="first_story", help="内置故事 ID")
    play_parser.add_argument("--story-file", help="从外部 JSON 文件加载故事")
    play_parser.add_argument("--mute", action="store_true", help="关闭背景音接口")

    subparsers.add_parser("list-stories", help="列出内置故事")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if args.command == "list-stories":
        for story_id in list_builtin_stories():
            console.print(story_id)
        return 0

    if args.story_file:
        story = load_story_from_path(Path(args.story_file))
    else:
        story = load_builtin_story(args.story)

    session = GameSession(
        story=story,
        renderer=StoryRenderer(console=console),
        audio_player=create_audio_player(enabled=not args.mute),
        muted=args.mute,
    )
    session.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
