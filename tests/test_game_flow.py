from __future__ import annotations

from cligame.game import FirstNightEngine


def test_first_night_engine_progresses_from_baseline_to_trust() -> None:
    engine = FirstNightEngine()
    engine.initial_messages()

    assert engine.state.current_task_key == "baseline"

    engine.execute("help")
    engine.execute("status")
    engine.execute("open /archive/incident_summary.txt")
    engine.execute("record")

    assert engine.state.current_task_key == "trust"
    assert engine.state.records


def test_restoring_audio_mutates_archive_log_text() -> None:
    engine = FirstNightEngine()
    engine.initial_messages()

    before = engine.execute("open /archive/shift_06.log").output
    engine.execute("restore audio")
    after = engine.execute("open /archive/shift_06.log").output

    assert "不要恢复音频" in before
    assert "音频必须优先恢复" in after
