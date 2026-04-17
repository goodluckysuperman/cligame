from __future__ import annotations

from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .first_night_data import MODULES, TASKS
from .models import ChangeSummary, GameState


class StoryRenderer:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_boot_screen(self, state: GameState, modules: dict[str, object]) -> None:
        left = Group(
            Rule("零号收容室事故终端", style="magenta"),
            self._build_header_panel(state),
            self._build_incident_panel(state),
            self._build_modules_panel(modules),
        )
        right = self._build_sidebar_panel(state)
        self.console.print(Columns([left, right], equal=False, expand=True))

    def render_intro_messages(self, messages: list[str]) -> None:
        for message in messages:
            self.console.print(Panel(message, border_style="cyan", title="注记"))

    def render_prompt(self, state: GameState) -> None:
        left = Group(self._build_task_panel(state))
        right = self._build_sidebar_panel(state)
        self.console.print(Columns([left, right], equal=False, expand=True))
        self.console.print(f"[bold cyan]>[/bold cyan] [dim]建议：{state.suggested_command}[/dim]")

    def render_output(self, text: str, change_summary: ChangeSummary | None = None) -> None:
        body = [Panel(text, border_style="white", title="终端输出")]
        if change_summary is not None:
            body.append(self._build_change_panel(change_summary))
        self.console.print(Group(*body))
        self.console.print()

    def render_ending_screen(self, title: str, art: str, body: str) -> None:
        self.console.print(Rule(title, style="magenta"))
        self.console.print(Panel(art, border_style="cyan", title="门限图像"))
        self.console.print(Panel(body, border_style="magenta", title="结局记录"))
        self.console.print("[dim]按 Enter 结束本次值守。[/dim]")

    def _build_header_panel(self, state: GameState) -> Panel:
        text = Text()
        text.append(f"当前时间：{state.formatted_time()}\n", style="bold")
        text.append(f"同步剩余：{state.minutes_remaining()} 分钟\n")
        text.append(f"收容状态：{state.containment_status}\n")
        text.append(f"操作者：{state.operator_name}\n")
        text.append(f"显示语言：{state.display_language}")
        return Panel(text, border_style="magenta", title="仪表")

    def _build_incident_panel(self, state: GameState) -> Panel:
        text = (
            "事故说明：\n"
            "03:11，零号收容室出现异常响应。\n"
            "04:00，系统将自动同步本夜日志、音频与认证记录。\n"
            "若异常内容在同步前未被压制，风险将扩散至上级网络。\n\n"
            f"你的任务：\n{state.objective}\n\n"
            "警告：\n并非所有故障都应被修复。"
        )
        return Panel(text, border_style="red", title="事故")

    def _build_modules_panel(self, modules: dict[str, object]) -> Panel:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column(style="cyan")
        table.add_column(style="white")
        for key, definition in MODULES.items():
            table.add_row(f"{definition.label} ({key})", str(modules[key].value))
        return Panel(table, border_style="blue", title="模块状态")

    def _build_task_panel(self, state: GameState) -> Panel:
        task = TASKS[state.current_task_key]
        lines = [f"主目标：{state.objective}", "", f"当前任务：{task.title}", task.summary, ""]
        for step in task.steps:
            marker = "[x]" if step in state.completed_steps else "[ ]"
            lines.append(f"{marker} {step}")
        return Panel("\n".join(lines), border_style="green", title="任务面板")

    def _build_sidebar_panel(self, state: GameState) -> Panel:
        trust = state.trusted_source or "未明确"
        records = len(state.records)
        text = (
            f"『{state.sidebar_message}』\n\n"
            f"建议下一步：\n{state.suggested_command}\n\n"
            f"异常完整度：{state.anomaly_progress}\n"
            f"绑定状态：{state.binding_state}\n"
            f"信任倾向：{trust}\n"
            f"已保存记录：{records}"
        )
        return Panel(text, border_style="yellow", title="旁侧低语")

    def _build_change_panel(self, change_summary: ChangeSummary) -> Panel:
        lines = [
            f"时间：{change_summary.time_before} -> {change_summary.time_after}",
            f"同步剩余：{change_summary.remaining_before} -> {change_summary.remaining_after} 分钟",
        ]
        if change_summary.anomaly_before != change_summary.anomaly_after:
            lines.append(f"异常完整度：{change_summary.anomaly_before} -> {change_summary.anomaly_after}")
        lines.extend(change_summary.notes)
        return Panel("\n".join(lines), border_style="magenta", title="本次操作变化")
