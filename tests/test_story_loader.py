from __future__ import annotations

from cligame.game import FirstNightEngine
from cligame.story_loader import list_builtin_stories


def test_list_builtin_stories_returns_first_night() -> None:
    assert list_builtin_stories() == ["first_night"]


def test_protocol_unlocks_after_auth_and_access_restore() -> None:
    engine = FirstNightEngine()
    engine.initial_messages()

    engine.execute("restore auth")
    engine.execute("restore access")
    output = engine.execute("protocols").output

    assert "threshold_reset" in output
    assert "可执行" in output
