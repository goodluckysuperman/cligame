from __future__ import annotations

from importlib import resources

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from .models import Story, StoryNode


class StoryRenderer:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_story_intro(self, story: Story, muted: bool) -> None:
        self.console.print(Panel.fit(story.title, style="bold magenta"))
        self.console.print(story.intro)
        audio_status = "已静音" if muted else "结束时将播放共享音效"
        self.console.print(f"[dim]{audio_status}[/dim]")
        self.console.print(Rule(style="blue"))

    def render_node(self, node: StoryNode) -> None:
        self.console.print(node.text)
        self.console.print()

    def render_choices(self, node: StoryNode) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="cyan", width=3)
        table.add_column(style="white")
        for index, choice in enumerate(node.choices, start=1):
            table.add_row(f"[{index}]", choice.label)
        self.console.print(table)

    def render_invalid_choice(self) -> None:
        self.console.print("[red]输入无效，请重新选择对应的编号。[/red]")

    def render_ending_screen(self, node: StoryNode, art_key: str) -> None:
        title = node.ending_title or "结局"
        body = node.ending or "故事结束。"
        art = self._load_ending_art(art_key)
        self.console.print(Rule(title, style="magenta"))
        self.console.print(f"[cyan]{art}[/cyan]")
        self.console.print(Panel(body, border_style="magenta"))
        self.console.print("[dim]按 Enter 结束本次夜行。[/dim]")

    def _load_ending_art(self, art_key: str) -> str:
        art_file = resources.files("cligame.content.art.endings").joinpath(f"{art_key}.txt")
        with art_file.open("r", encoding="utf-8") as handle:
            return handle.read().rstrip()
