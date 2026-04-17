from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Choice:
    label: str
    next_node: str
    tag: str | None = None


@dataclass(frozen=True)
class StoryNode:
    node_id: str
    text: str
    choices: tuple[Choice, ...] = field(default_factory=tuple)
    ending: str | None = None
    ending_title: str | None = None
    ending_art: str | None = None

    @property
    def is_ending(self) -> bool:
        return self.ending is not None


@dataclass(frozen=True)
class Story:
    story_id: str
    title: str
    intro: str
    start_node: str
    nodes: dict[str, StoryNode]

    def get_node(self, node_id: str) -> StoryNode:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise ValueError(f"Unknown node id: {node_id}") from exc
