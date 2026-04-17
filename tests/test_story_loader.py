from __future__ import annotations

from cligame.story_loader import StoryValidationError, list_builtin_stories, load_builtin_story, load_story_from_dict


def test_list_builtin_stories_includes_first_story() -> None:
    assert "first_story" in list_builtin_stories()


def test_load_builtin_story_has_expected_start_node() -> None:
    story = load_builtin_story("first_story")
    assert story.story_id == "first_story"
    assert story.start_node == "bell_tower"
    assert story.get_node("ending_sealed").is_ending is True
    assert story.get_node("ending_sealed").ending_art == "ending_sealed"


def test_invalid_story_requires_known_next_node() -> None:
    invalid_story = {
        "id": "broken",
        "title": "Broken",
        "intro": "...",
        "start_node": "start",
        "nodes": [
            {
                "id": "start",
                "text": "Broken node",
                "choices": [{"label": "Go", "next": "missing"}],
            }
        ],
    }

    try:
        load_story_from_dict(invalid_story)
    except StoryValidationError as exc:
        assert "unknown next node" in str(exc)
    else:
        raise AssertionError("Expected StoryValidationError")
