from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from .first_night_data import TASKS
from .models import ChangeSummary, GameState


class StoryRenderer:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_boot_screen(self, state: GameState, modules: dict[str, object]) -> None:
        self.console.print("=" * 60)
        self.console.print("零号收容室事故终端")
        self.console.print(
            f"当前时间：{state.formatted_time()}               同步剩余：{state.minutes_remaining()} 分钟\n"
            f"收容状态：{state.containment_status}               操作者：{state.operator_name}\n"
            f"显示语言：{state.display_language}"
        )
        self.console.print("=" * 60)
        self.console.print()
        self.console.print("事故说明：")
        self.console.print("03:11，零号收容室出现异常响应。")
        self.console.print("04:00，系统将自动同步本夜日志、音频与认证记录。")
        self.console.print("若异常内容在同步前未被压制，风险将扩散至上级网络。")
        self.console.print()
        self.console.print("你的任务：")
        self.console.print(state.objective)
        self.console.print()
        self.console.print("警告：")
        self.console.print("并非所有故障都应被修复。")
        self.console.print()
        self.console.print("新手指引：")
        self.console.print("先输入 status 查看事故总览。")
        self.console.print("（输入请统一使用英文命令）")

    def render_intro_messages(self, messages: list[str]) -> None:
        for message in messages:
            self.console.print(Panel(message, border_style="cyan"))

    def render_prompt(self, state: GameState) -> None:
        task = TASKS[state.current_task_key]
        self.console.print(
            f"[dim]{state.formatted_time()} | 剩余 {state.minutes_remaining()} 分钟 | 当前任务：{task.title}[/dim]"
        )
        self.console.print(f"[dim]当前目标：{state.objective}[/dim]")
        self.console.print(f"[dim]建议下一步：输入 {state.suggested_command}[/dim]")
        if state.proactive_messages:
            for message in state.proactive_messages:
                self.console.print(Panel(message, border_style="yellow"))
            state.proactive_messages.clear()

    def render_output(self, text: str, change_summary: ChangeSummary | None = None) -> None:
        self.console.print(text)
        if change_summary is not None:
            self.console.print()
            self.console.print("[bold]本次操作变化：[/bold]")
            self.console.print(
                f"- 时间：{change_summary.time_before} -> {change_summary.time_after}"
            )
            self.console.print(
                f"- 同步剩余：{change_summary.remaining_before} -> {change_summary.remaining_after} 分钟"
            )
            if change_summary.anomaly_before != change_summary.anomaly_after:
                self.console.print(
                    f"- 异常完整度：{change_summary.anomaly_before} -> {change_summary.anomaly_after}"
                )
            for note in change_summary.notes:
                self.console.print(f"- {note}")
        self.console.print()

    def render_ending_screen(self, title: str, art: str, body: str) -> None:
        self.console.print(Rule(title, style="magenta"))
        self.console.print(f"[cyan]{art}[/cyan]")
        self.console.print(Panel(body, border_style="magenta"))
        self.console.print("[dim]按 Enter 结束本次值守。[/dim]")
