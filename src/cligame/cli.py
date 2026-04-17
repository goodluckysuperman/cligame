from __future__ import annotations

import argparse

from rich.console import Console

from .audio import create_audio_player
from .game import FirstNightEngine
from .renderer import StoryRenderer


BGM_TRACK = "bgm/background_loop.mp3"
ENDING_TRACK = "endings/shared_ending.mp3"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cligame", description="门限协议 / Threshold Protocol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    play_parser = subparsers.add_parser("play", help="开始第一夜")
    play_parser.add_argument("--mute", action="store_true", help="关闭背景音乐和结束音效")

    subparsers.add_parser("list-stories", help="列出当前可玩的内容")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if args.command == "list-stories":
        console.print("first_night")
        return 0

    engine = FirstNightEngine()
    renderer = StoryRenderer(console=console)
    audio_player = create_audio_player(enabled=not args.mute)

    try:
        renderer.render_boot_screen(engine.state, engine.modules)
        renderer.render_intro_messages(engine.initial_messages())
        if not args.mute:
            audio_player.start_bgm(BGM_TRACK)

        while not engine.state.finished:
            renderer.render_prompt(engine.state)
            raw_command = input("> ")
            result = engine.execute(raw_command)
            renderer.render_output(result.output, engine.last_change_summary)

        if not args.mute:
            audio_player.play_ending(ENDING_TRACK)
        renderer.render_ending_screen(
            engine.state.ending_title or "结局",
            engine.state.ending_art or "",
            engine.state.ending_body or "",
        )
        input("")
        return 0
    except KeyboardInterrupt:
        console.print("\n[dim]已中断当前值守。[/dim]")
        return 130
    except EOFError:
        console.print("\n[dim]输入流已结束，正在退出。[/dim]")
        return 0
    finally:
        audio_player.stop_bgm()


if __name__ == "__main__":
    raise SystemExit(main())
