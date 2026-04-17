from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .audio import AudioPlayer
from .models import Choice, Story, StoryNode
from .renderer import StoryRenderer

InputHandler = Callable[[str], str]

SHARED_ENDING_TRACK = "endings/shared_ending.mp3"
DEFAULT_ENDING_ART = "ending_marked"


@dataclass
class GameSession:
    story: Story
    renderer: StoryRenderer
    input_handler: InputHandler = input
    audio_player: AudioPlayer | None = None
    muted: bool = False

    def run(self) -> None:
        try:
            self.renderer.render_story_intro(self.story, muted=self.muted)
            current_node = self.story.get_node(self.story.start_node)

            while True:
                self.renderer.render_node(current_node)
                if current_node.is_ending:
                    self._run_ending(current_node)
                    return

                self.renderer.render_choices(current_node)
                selected_choice = self._prompt_choice(current_node)
                current_node = self.story.get_node(selected_choice.next_node)
        finally:
            if self.audio_player is not None:
                self.audio_player.stop_bgm()

    def _run_ending(self, node: StoryNode) -> None:
        art_key = node.ending_art or DEFAULT_ENDING_ART
        if not self.muted and self.audio_player is not None:
            self.audio_player.play_ending(SHARED_ENDING_TRACK)
        self.renderer.render_ending_screen(node, art_key)
        self.input_handler("")

    def _prompt_choice(self, node: StoryNode) -> Choice:
        while True:
            raw_value = self.input_handler("请选择编号: ").strip()
            if raw_value.isdigit():
                selected_index = int(raw_value) - 1
                if 0 <= selected_index < len(node.choices):
                    return node.choices[selected_index]
            self.renderer.render_invalid_choice()
