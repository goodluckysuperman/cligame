from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from .models import Choice, Story, StoryNode


class StoryValidationError(ValueError):
    pass


def load_builtin_story(story_id: str) -> Story:
    package_file = resources.files("cligame.content.stories").joinpath(f"{story_id}.json")
    with package_file.open("r", encoding="utf-8") as handle:
        return load_story_from_dict(json.load(handle))


def load_story_from_path(path: str | Path) -> Story:
    with Path(path).open("r", encoding="utf-8") as handle:
        return load_story_from_dict(json.load(handle))


def list_builtin_stories() -> list[str]:
    stories_dir = resources.files("cligame.content.stories")
    return sorted(path.stem for path in stories_dir.iterdir() if path.suffix == ".json")


def load_story_from_dict(data: dict) -> Story:
    required_fields = {"id", "title", "intro", "start_node", "nodes"}
    missing = required_fields - data.keys()
    if missing:
        raise StoryValidationError(f"Story is missing fields: {sorted(missing)}")

    raw_nodes = data["nodes"]
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise StoryValidationError("Story must define a non-empty node list")

    nodes: dict[str, StoryNode] = {}
    for raw_node in raw_nodes:
        node_id = raw_node["id"]
        raw_choices = raw_node.get("choices", [])
        choices = tuple(
            Choice(
                label=raw_choice["label"],
                next_node=raw_choice["next"],
                tag=raw_choice.get("tag"),
            )
            for raw_choice in raw_choices
        )
        node = StoryNode(
            node_id=node_id,
            text=raw_node["text"],
            choices=choices,
            ending=raw_node.get("ending"),
            ending_title=raw_node.get("ending_title"),
            ending_art=raw_node.get("ending_art"),
        )
        if node.is_ending and node.choices:
            raise StoryValidationError(f"Ending node '{node_id}' cannot define choices")
        if not node.is_ending and not node.choices:
            raise StoryValidationError(f"Non-ending node '{node_id}' must define choices")
        nodes[node_id] = node

    start_node = data["start_node"]
    if start_node not in nodes:
        raise StoryValidationError(f"Unknown start_node: {start_node}")

    for node in nodes.values():
        for choice in node.choices:
            if choice.next_node not in nodes:
                raise StoryValidationError(
                    f"Node '{node.node_id}' points to unknown next node '{choice.next_node}'"
                )

    return Story(
        story_id=data["id"],
        title=data["title"],
        intro=data["intro"],
        start_node=start_node,
        nodes=nodes,
    )
