from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ModuleStatus(str, Enum):
    OFFLINE = "离线"
    CORRUPTED = "损坏"
    DEGRADED = "降级"
    RESTRICTED = "受限"
    RESTORED = "已恢复"
    ISOLATED = "已隔离"


@dataclass(frozen=True)
class ModuleDefinition:
    key: str
    label: str
    initial_status: ModuleStatus
    restore_minutes: int
    isolate_minutes: int
    restore_summary: str
    isolate_summary: str


@dataclass(frozen=True)
class TaskDefinition:
    key: str
    title: str
    summary: str
    steps: tuple[str, ...]


@dataclass(frozen=True)
class ProtocolDefinition:
    key: str
    label: str
    summary: str
    requirement_text: str
    ending_text: str
    cost_text: str


@dataclass(frozen=True)
class RelayMessage:
    sender: str
    time_label: str
    body: str


@dataclass
class ChangeSummary:
    time_before: str
    time_after: str
    remaining_before: int
    remaining_after: int
    anomaly_before: int
    anomaly_after: int
    notes: list[str] = field(default_factory=list)


@dataclass
class GameState:
    current_time_minutes: int = 3 * 60 + 17
    deadline_minutes: int = 4 * 60
    objective: str = "在 04:00 前，执行一项收容方案。"
    containment_status: str = "不稳定"
    anomaly_level: str = "中"
    display_language: str = "中文"
    operator_name: str = "未认证"
    binding_state: str = "无"
    threshold_state: str = "未知"
    current_task_key: str = "baseline"
    completed_steps: set[str] = field(default_factory=set)
    tutorial_step: int = 0
    suggested_command: str = "status"
    onboarding_active: bool = True
    inventory: list[str] = field(default_factory=list)
    records: dict[str, str] = field(default_factory=dict)
    command_history: list[str] = field(default_factory=list)
    trusted_source: str | None = None
    anomaly_progress: int = 0
    insight_level: int = 0
    senior_stage: int = 0
    auth_trace_unlocked: bool = False
    protocols_unlocked: set[str] = field(default_factory=set)
    finished: bool = False
    ending_title: str | None = None
    ending_body: str | None = None
    ending_art: str | None = None
    proactive_messages: list[str] = field(default_factory=list)
    sidebar_message: str = "先确认事故总览。你现在最需要的不是勇气，是证据。"

    def minutes_remaining(self) -> int:
        return max(0, self.deadline_minutes - self.current_time_minutes)

    def advance_time(self, minutes: int) -> None:
        self.current_time_minutes += minutes

    def formatted_time(self) -> str:
        hour = self.current_time_minutes // 60
        minute = self.current_time_minutes % 60
        return f"{hour:02d}:{minute:02d}"
