from __future__ import annotations

from rich.console import Console

from cligame.audio import NoopAudioPlayer
from cligame.game import GameSession
from cligame.renderer import StoryRenderer
from cligame.story_loader import load_builtin_story


def test_game_session_reprompts_on_invalid_choice() -> None:
    story = load_builtin_story("first_story")
    inputs = iter(["x", "1", "2", "1", ""])
    output_console = Console(record=True, width=100)
    audio = NoopAudioPlayer()
    session = GameSession(
        story=story,
        renderer=StoryRenderer(console=output_console),
        input_handler=lambda _: next(inputs),
        audio_player=audio,
    )

    session.run()

    exported = output_console.export_text()
    assert "输入无效" in exported
    assert "结局：守夜人" in exported
    assert "按 Enter 结束本次夜行" in exported
    assert audio.current_track is None
