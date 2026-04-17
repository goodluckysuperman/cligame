from __future__ import annotations

from dataclasses import dataclass
from importlib import resources

from .first_night_data import MODULES, PROTOCOLS, RELAY_MESSAGES, SENIOR_MESSAGES, TASKS
from .models import ChangeSummary, GameState, ModuleStatus, ProtocolDefinition


@dataclass
class CommandResult:
    output: str
    consume_minutes: int = 0
    notes: list[str] | None = None


class FirstNightEngine:
    def __init__(self) -> None:
        self.state = GameState()
        self.modules = {key: definition.initial_status for key, definition in MODULES.items()}
        self.seen_files: dict[str, int] = {}
        self.last_change_summary: ChangeSummary | None = None

    def initial_messages(self) -> list[str]:
        self.state.inventory.append("离线记录器")
        self.state.suggested_command = "status"
        return [
            SENIOR_MESSAGES[0],
            "前辈已将【离线记录器】交给你。它能保存当前证据快照，之后你会用它确认文件是否被改写。",
        ]

    def execute(self, raw_command: str) -> CommandResult:
        command = raw_command.strip()
        if not command:
            self.last_change_summary = None
            return CommandResult("请输入命令。")

        time_before = self.state.formatted_time()
        remaining_before = self.state.minutes_remaining()
        anomaly_before = self.state.anomaly_progress
        notes: list[str] = []

        self.state.command_history.append(command)
        parts = command.split()
        verb = parts[0].lower()
        arg = " ".join(parts[1:]) if len(parts) > 1 else ""

        handlers = {
            "help": self._help,
            "status": self._status,
            "modules": self._modules,
            "check": self._check,
            "talk": self._talk,
            "ls": self._ls,
            "open": self._open,
            "whoami": self._whoami,
            "record": self._record,
            "records": self._records,
            "compare": self._compare,
            "relay": self._relay,
            "reply": self._reply,
            "scan": self._scan,
            "restore": self._restore,
            "isolate": self._isolate,
            "inventory": self._inventory,
            "protocols": self._protocols,
            "execute": self._execute_protocol,
            "history": self._history,
        }

        handler = handlers.get(verb)
        if handler is None:
            self.state.sidebar_message = "先别乱试。先按我说的顺序来。输入 help，看基础命令。"
            self.last_change_summary = None
            return CommandResult("未知命令。输入 help 查看可用命令。")

        result = handler(arg)
        if result.notes:
            notes.extend(result.notes)

        if result.consume_minutes:
            self.state.advance_time(result.consume_minutes)

        notes.extend(self._post_action_updates(command))

        if self.state.current_time_minutes >= self.state.deadline_minutes and not self.state.finished:
            self._trigger_timeout_failure()
            notes.append("04:00 已到。系统强制进入失败结局。")

        self.last_change_summary = ChangeSummary(
            time_before=time_before,
            time_after=self.state.formatted_time(),
            remaining_before=remaining_before,
            remaining_after=self.state.minutes_remaining(),
            anomaly_before=anomaly_before,
            anomaly_after=self.state.anomaly_progress,
            notes=notes,
        )
        return result

    def _help(self, _: str) -> CommandResult:
        self.state.suggested_command = "status"
        self.state.sidebar_message = "对，就是这样。先看清事故总览，再决定碰哪里。下一步输入 status。"
        self._complete_step("查看事故总览", pending=True)
        return CommandResult(
            "【帮助】\n统一使用英文命令输入。\n可用命令：help status modules check task talk senior ls open scan relay reply whoami record records compare inventory restore isolate protocols execute <key> history"
        )

    def _status(self, _: str) -> CommandResult:
        self.state.suggested_command = "modules"
        self.state.sidebar_message = "很好。你现在知道事故确实存在了。下一步看 modules，先确认哪些故障是真的坏，哪些可能是主动切断。"
        self._complete_step("查看事故总览")
        return CommandResult(
            "当前时间：{}\n同步剩余：{} 分钟\n异常等级：{}\n收容状态：{}\n操作者：{}\n\n当前目标：\n1. 查明异常来源\n2. 评估可恢复模块\n3. 在 04:00 前执行收容方案\n\n建议下一步：\n输入 modules 查看模块状态。".format(
                self.state.formatted_time(),
                self.state.minutes_remaining(),
                self.state.anomaly_level,
                self.state.containment_status,
                self.state.operator_name,
            )
        )

    def _modules(self, _: str) -> CommandResult:
        self.state.suggested_command = "ls /archive"
        self.state.sidebar_message = "记住：不是所有故障都应该修。先查档案。下一步输入 ls /archive。"
        self._complete_step("查看模块状态")
        lines = [
            "模块状态如下：",
            "",
            f"音频 (audio)    {self.modules['audio'].value}",
            f"监控 (camera)   {self.modules['camera'].value}",
            f"档案 (archive)  {self.modules['archive'].value}",
            f"门禁 (lock)     {self.modules['lock'].value}",
            f"权限 (auth)     {self.modules['auth'].value}",
            "",
            "说明：",
            "离线：当前不可用",
            "损坏：可部分读取",
            "降级：可用但不完整",
            "受限：需要额外条件",
            "",
            "建议下一步：",
            "输入 ls /archive 查看事故档案。",
        ]
        return CommandResult("\n".join(lines))

    def _check(self, arg: str) -> CommandResult:
        if arg != "task":
            return CommandResult("当前只支持 check task。")
        task = TASKS[self.state.current_task_key]
        steps = []
        for step in task.steps:
            marker = "[x]" if step in self.state.completed_steps else "[ ]"
            steps.append(f"{marker} {step}")
        return CommandResult(f"{task.title}\n{task.summary}\n" + "\n".join(steps))

    def _talk(self, arg: str) -> CommandResult:
        if arg != "senior":
            return CommandResult("现在只能 talk senior。")
        return CommandResult(self.state.sidebar_message)

    def _ls(self, arg: str) -> CommandResult:
        mapping = {
            "/archive": ["incident_summary.txt", "shift_06.log", "operator_memo.txt", "handbook.txt"],
            "/audio": ["residual_trace.txt"] if self.modules["audio"] == ModuleStatus.RESTORED else [],
            "/camera": ["frame_B.txt"] if self.modules["camera"] == ModuleStatus.RESTORED else [],
            "/auth": ["identity_map.redacted"] if self.modules["auth"] == ModuleStatus.RESTORED else [],
            "/protocols": ["threshold_protocol.txt"] if "threshold_protocol.txt" in self.state.protocols_unlocked else [],
        }
        files = mapping.get(arg)
        if files is None:
            return CommandResult("目录不存在。", consume_minutes=1)
        if not files:
            return CommandResult(f"{arg} 为空或尚未解锁。", consume_minutes=1)
        if arg == "/archive":
            self.state.suggested_command = "open /archive/incident_summary.txt"
            self.state.sidebar_message = "很好，事故档案还在。先读事故摘要，不要先碰日志。你需要先知道系统认为发生了什么。"
            self._complete_step("查看模块状态", pending=True)
            text = "/archive 目录内容：\n\n" + "\n".join(files) + "\n\n建议下一步：\n输入 open /archive/incident_summary.txt 阅读事故摘要。"
            return CommandResult(text, consume_minutes=1)
        return CommandResult("\n".join(files), consume_minutes=1)

    def _open(self, arg: str) -> CommandResult:
        file_map = {
            "/archive/incident_summary.txt": "archive/incident_summary.txt",
            "/archive/shift_06.log": "archive/shift_06.log",
            "/archive/operator_memo.txt": "archive/operator_memo.txt",
            "/archive/handbook.txt": "archive/handbook.txt",
            "/audio/residual_trace.txt": "audio/residual_trace.txt",
            "/camera/frame_B.txt": "camera/frame_B.txt",
            "/auth/identity_map.redacted": "auth/identity_map.redacted",
            "/protocols/threshold_protocol.txt": "protocols/threshold_protocol.txt",
        }
        relative_path = file_map.get(arg)
        if relative_path is None:
            return CommandResult("文件不存在。", consume_minutes=1)
        if arg.startswith("/audio") and self.modules["audio"] != ModuleStatus.RESTORED:
            return CommandResult("音频模块未恢复，无法读取该文件。", consume_minutes=1)
        if arg.startswith("/camera") and self.modules["camera"] != ModuleStatus.RESTORED:
            return CommandResult("监控模块未恢复，无法读取该文件。", consume_minutes=1)
        if arg.startswith("/auth") and self.modules["auth"] != ModuleStatus.RESTORED:
            return CommandResult("权限模块未恢复，无法读取该文件。", consume_minutes=1)
        if arg.startswith("/protocols") and "threshold_protocol.txt" not in self.state.protocols_unlocked:
            return CommandResult("协议尚未解锁。", consume_minutes=1)

        content = self._read_file(relative_path)
        self.seen_files[arg] = self.seen_files.get(arg, 0) + 1
        notes: list[str] = []
        if arg == "/archive/incident_summary.txt":
            self.state.suggested_command = "scan audio"
            self.state.sidebar_message = "现在你知道这些故障可能是主动隔离措施。别急着修，先低风险扫描。下一步输入 scan audio。"
            self._complete_step("读取事故摘要")
            content = "【事故摘要】\n\n" + content + "\n\n建议下一步：\n输入 scan audio 对音频模块做低风险扫描。"
        elif arg == "/archive/shift_06.log":
            self.state.sidebar_message = "这就是问题开始复杂的地方。旧日志和当前指令很可能会冲突。你现在得开始判断该信谁。"
            if self.state.current_task_key == "baseline":
                self.state.current_task_key = "trust"
                notes.append("任务阶段已切换：你开始接触互相冲突的信息源。")
        elif arg == "/auth/identity_map.redacted":
            self.state.sidebar_message = "系统正在用身份层重新定义你。现在你已经不是纯旁观者了。"
        return CommandResult(content, consume_minutes=1, notes=notes)

    def _whoami(self, _: str) -> CommandResult:
        self.state.suggested_command = "record"
        self.state.sidebar_message = "确认你自己是谁。之后立刻保存第一份快照。等文件开始变，你就会明白为什么这一步不能跳。"
        self._complete_step("确认操作者身份")
        return CommandResult(
            f"操作者：{self.state.operator_name}\n绑定状态：{self.state.binding_state}\n门限适配：{self.state.threshold_state}\n\n建议下一步：\n输入 record 保存第一份证据快照。",
            consume_minutes=1,
        )

    def _record(self, _: str) -> CommandResult:
        snapshot = [
            f"time={self.state.formatted_time()}",
            f"operator={self.state.operator_name}",
            f"binding={self.state.binding_state}",
            f"anomaly={self.state.anomaly_progress}",
        ]
        for key, status in self.modules.items():
            snapshot.append(f"module.{key}={status.value}")
        record_name = f"record-{len(self.state.records) + 1}"
        self.state.records[record_name] = "\n".join(snapshot)
        self.state.current_task_key = "trust"
        self.state.suggested_command = "relay"
        self.state.onboarding_active = False
        self.state.sidebar_message = "很好。现在你终于有了第一份不会跟着系统一起变的证据。接下来去看远程通讯，冲突马上就会出现。"
        self._complete_step("保存第一份离线记录")
        return CommandResult(
            "离线记录已保存。\n\n你现在已经有了第一份可回溯证据。\n建议下一步：\n输入 relay 查看远程通讯。",
            consume_minutes=1,
            notes=["引导结束。从现在开始，你需要自己判断下一步操作。"],
        )

    def _records(self, _: str) -> CommandResult:
        if not self.state.records:
            return CommandResult("当前没有已保存记录。")
        names = "\n".join(self.state.records.keys())
        return CommandResult(f"已保存记录：\n{names}")

    def _compare(self, arg: str) -> CommandResult:
        parts = arg.split()
        if len(parts) != 2:
            return CommandResult("用法：compare <record-name> <file-path>")
        record_name, file_path = parts
        record = self.state.records.get(record_name)
        if record is None:
            return CommandResult("找不到该记录。")
        if file_path != "/archive/shift_06.log":
            return CommandResult("当前仅支持对比 /archive/shift_06.log。")
        current = self._read_file("archive/shift_06.log")
        if record == current:
            return CommandResult("记录与当前文件一致。")
        self.state.sidebar_message = "看见了吗？它已经开始改写文本了。从这一刻起，你不能再只信终端显示出来的东西。"
        return CommandResult("对比结果：当前文件与记录不一致。\n说明：档案内容已发生变化。", consume_minutes=1, notes=["你确认了一次文本篡改。"])

    def _relay(self, _: str) -> CommandResult:
        self.state.suggested_command = "reply remote"
        self.state.sidebar_message = "远程支援终于冒头了。现在开始，你必须决定先信谁。"
        self._complete_step("查看远程通讯")
        messages = "【远程通讯】\n\n" + "\n\n".join(f"[{item.time_label}][{item.sender}]\n{item.body}" for item in RELAY_MESSAGES)
        messages += "\n\n引导结束。\n从现在开始，你可以自行决定下一步操作。\n\n常见选择：\nopen /archive/shift_06.log\nrestore audio\nscan archive\nhelp"
        return CommandResult(messages, consume_minutes=1)

    def _reply(self, arg: str) -> CommandResult:
        target = arg or "remote"
        if "remote" in target or "远程" in target:
            self.state.trusted_source = "remote"
            self.state.anomaly_progress += 1
            self.state.suggested_command = "restore audio"
            self.state.sidebar_message = "你选择先信远程。那就准备好承担更快的异常增长。"
            return CommandResult("你向远程支援回复：收到。我会优先考虑恢复 audio。", consume_minutes=1, notes=["信任倾向：远程支援"])
        if "senior" in target or "前辈" in target:
            self.state.trusted_source = "senior"
            self.state.suggested_command = "open /archive/shift_06.log"
            self.state.sidebar_message = "你选择先信旁侧低语。那就沿着证据链继续下去，别急着恢复高风险模块。"
            return CommandResult("你向前辈确认：我会先建立证据链，不盲目修复。", consume_minutes=1, notes=["信任倾向：前辈"])
        return CommandResult("通讯目标无响应。", consume_minutes=1)

    def _scan(self, arg: str) -> CommandResult:
        if arg == "audio":
            self.state.suggested_command = "relay"
            self.state.sidebar_message = "音频模块是第一道真正的风险门。它能给你线索，也能让它重新获得声音。"
            return CommandResult(
                "【模块扫描：音频】\n\n当前状态：离线\n残留检测：存在低频信号\n恢复收益：可读取音频线索\n恢复风险：未知信号可能重新获得广播能力\n\n此刻收到一条远程消息。\n建议输入 relay 查看通讯。",
                consume_minutes=1,
            )
        if arg == "archive":
            return CommandResult("【模块扫描：档案】\n\n当前状态：损坏\n恢复收益：可读取更多事故记录\n恢复风险：部分文档可能开始自我改写。", consume_minutes=1)
        if arg == "camera":
            return CommandResult("【模块扫描：监控】\n\n当前状态：离线\n恢复收益：获取零号收容室视觉证据\n恢复风险：观测可能是双向的。", consume_minutes=1)
        if arg == "lock":
            return CommandResult("【模块扫描：门禁】\n\n当前状态：降级\n恢复收益：开放更高阶协议路径\n恢复风险：门限逻辑可能因此重写。", consume_minutes=1)
        if arg == "auth":
            return CommandResult("【模块扫描：权限】\n\n当前状态：受限\n恢复收益：可接触更深权限文件\n恢复风险：系统将更明确地定义你是谁。", consume_minutes=1)
        return CommandResult("未知模块。", consume_minutes=1)

    def _restore(self, arg: str) -> CommandResult:
        module = MODULES.get(arg)
        if module is None:
            return CommandResult("未知模块。", consume_minutes=1)
        before_status = self.modules[arg]
        self.modules[arg] = ModuleStatus.RESTORED
        notes = [f"模块状态：{MODULES[arg].label} {before_status.value} -> 已恢复"]
        if arg == "audio":
            self.state.anomaly_progress += 2
            notes.append("新文件解锁：/audio/residual_trace.txt")
            self.state.sidebar_message = "你让它重新获得了广播能力。记住，这不是纯线索，而是一次交换。"
        elif arg == "archive":
            self.state.insight_level += 1
            notes.append("档案索引恢复，后续可见内容将增多。")
            self.state.sidebar_message = "档案会告诉你更多过去，但过去未必愿意保持原样。"
        elif arg == "camera":
            self.state.insight_level += 1
            self.state.anomaly_progress += 1
            notes.append("新文件解锁：/camera/frame_B.txt")
            self.state.sidebar_message = "你开始看见 Chamber-0 了。但别忘了，观测有时候是双向的。"
        elif arg == "auth":
            self.state.operator_name = "林某"
            self.state.binding_state = "进行中"
            self.state.threshold_state = "待确认"
            self.state.auth_trace_unlocked = True
            notes.append("身份变化：操作者被系统写入当前配置。")
            notes.append("新文件解锁：/auth/identity_map.redacted")
            self.state.sidebar_message = "我提醒过你，AUTH 不是纯权限层。它会把你写进事故里。"
        elif arg == "lock":
            self.state.protocols_unlocked.add("threshold_protocol.txt")
            notes.append("协议线索解锁：/protocols/threshold_protocol.txt")
            self.state.sidebar_message = "门禁一旦恢复，你离最终协议就更近了，也离真正的门更近了。"
        if self.state.current_task_key == "trust":
            self.state.current_task_key = "protocol"
            notes.append("任务阶段已进入：你必须开始考虑最终协议。")
        self.state.suggested_command = "protocols"
        return CommandResult(module.restore_summary, consume_minutes=module.restore_minutes, notes=notes)

    def _isolate(self, arg: str) -> CommandResult:
        module = MODULES.get(arg)
        if module is None:
            return CommandResult("未知模块。", consume_minutes=1)
        before_status = self.modules[arg]
        self.modules[arg] = ModuleStatus.ISOLATED
        notes = [f"模块状态：{MODULES[arg].label} {before_status.value} -> 已隔离"]
        if arg == "auth":
            self.state.binding_state = "无"
            notes.append("绑定状态已回落。")
        self.state.suggested_command = "modules"
        self.state.sidebar_message = "你选择了切断，而不是修复。记住，保守也许不是懦弱，而是另一种收容方式。"
        return CommandResult(module.isolate_summary, consume_minutes=module.isolate_minutes, notes=notes)

    def _inventory(self, _: str) -> CommandResult:
        return CommandResult("背包：\n" + "\n".join(f"- {item}" for item in self.state.inventory))

    def _protocols(self, _: str) -> CommandResult:
        lines = ["可执行协议概览："]
        for protocol in PROTOCOLS.values():
            available = self._protocol_available(protocol)
            marker = "可执行" if available else "未满足条件"
            lines.append(f"- {protocol.key} / {protocol.label}：{marker}；{protocol.summary}")
        return CommandResult("\n".join(lines))

    def _execute_protocol(self, arg: str) -> CommandResult:
        protocol = PROTOCOLS.get(arg)
        if protocol is None:
            return CommandResult("未知协议。")
        if not self._protocol_available(protocol):
            return CommandResult("该协议条件尚未满足。")
        self.state.finished = True
        self.state.ending_title = protocol.label
        self.state.ending_body = self._build_ending_body(protocol)
        self.state.ending_art = self._load_ending_art(self._protocol_art(protocol.key))
        return CommandResult(f"协议 {protocol.label} 已执行。")

    def _history(self, _: str) -> CommandResult:
        if not self.state.command_history:
            return CommandResult("尚无历史命令。")
        return CommandResult("\n".join(self.state.command_history[-12:]))

    def _post_action_updates(self, command: str) -> list[str]:
        notes: list[str] = []
        if self.state.minutes_remaining() <= 20 and self.state.sidebar_message.startswith("对，就是这样") is False:
            self.state.sidebar_message = "剩余时间已经低于 20 分钟。现在开始，你不是在找完美答案，而是在避免最坏结果。"
        if self.state.anomaly_progress >= 2 and self.state.operator_name == "未认证":
            self.state.operator_name = "林某"
            self.state.binding_state = "进行中"
            self.state.threshold_state = "待确认"
            notes.append("身份变化：系统开始用具体身份称呼你。")
        self._refresh_anomaly_labels()
        self._update_tutorial(command)
        if self.state.current_task_key == "protocol" and self.modules["auth"] == ModuleStatus.RESTORED and self.modules["lock"] == ModuleStatus.RESTORED:
            self.state.threshold_state = "通过"
            self.state.binding_state = "已确认"
            self.state.protocols_unlocked.add("threshold_protocol.txt")
            notes.append("门限适配：通过")
        return notes

    def _update_tutorial(self, command: str) -> None:
        chain = ["status", "modules", "ls /archive", "open /archive/incident_summary.txt", "scan audio", "relay"]
        if self.state.onboarding_active and self.state.tutorial_step < len(chain) and command == chain[self.state.tutorial_step]:
            self.state.tutorial_step += 1
            if self.state.tutorial_step < len(chain):
                self.state.suggested_command = chain[self.state.tutorial_step]

    def _refresh_anomaly_labels(self) -> None:
        if self.state.anomaly_progress <= 1:
            self.state.anomaly_level = "中"
            self.state.containment_status = "不稳定"
        elif self.state.anomaly_progress <= 3:
            self.state.anomaly_level = "高"
            self.state.containment_status = "恶化中"
        else:
            self.state.anomaly_level = "极高"
            self.state.containment_status = "临界"

    def _protocol_available(self, protocol: ProtocolDefinition) -> bool:
        if protocol.key == "minimum_lockdown":
            return True
        if protocol.key == "identity_cutoff":
            return self.modules["auth"] == ModuleStatus.RESTORED and self.state.anomaly_progress <= 3
        if protocol.key == "forced_purge":
            return self.modules["auth"] == ModuleStatus.RESTORED or self.state.trusted_source == "remote"
        if protocol.key == "threshold_reset":
            return self.modules["auth"] == ModuleStatus.RESTORED and self.modules["lock"] == ModuleStatus.RESTORED
        return False

    def _protocol_art(self, key: str) -> str:
        art = {
            "minimum_lockdown": "ending_flight",
            "identity_cutoff": "ending_sealed",
            "forced_purge": "ending_whisper",
            "threshold_reset": "ending_marked",
        }
        return art[key]

    def _load_ending_art(self, art_key: str) -> str:
        art_file = resources.files("cligame.content.art.endings").joinpath(f"{art_key}.txt")
        with art_file.open("r", encoding="utf-8") as handle:
            return handle.read().rstrip()

    def _build_ending_body(self, protocol: ProtocolDefinition) -> str:
        restored = [MODULES[key].label for key, status in self.modules.items() if status == ModuleStatus.RESTORED]
        return (
            f"{protocol.ending_text}\n\n"
            f"代价：{protocol.cost_text}\n\n"
            f"结局总结：\n"
            f"- 你信任的对象：{self.state.trusted_source or '尚未明确表态'}\n"
            f"- 已恢复模块：{', '.join(restored) if restored else '无'}\n"
            f"- 已保存记录：{len(self.state.records)}\n"
            f"- 最终绑定状态：{self.state.binding_state}"
        )

    def _trigger_timeout_failure(self) -> None:
        self.state.finished = True
        self.state.ending_title = "同步失败"
        self.state.ending_art = self._load_ending_art("ending_whisper")
        restored = [MODULES[key].label for key, status in self.modules.items() if status == ModuleStatus.RESTORED]
        self.state.ending_body = (
            "04:00 已到。系统开始自动同步本夜日志、音频与认证记录。你还没来得及执行最终协议，异常内容已经越过了设施边界。\n\n"
            f"你最后恢复的模块：{', '.join(restored) if restored else '无'}\n"
            f"你最终的绑定状态：{self.state.binding_state}\n"
            "这一次，你没有来得及替任何人关上门。"
        )

    def _read_file(self, relative_path: str) -> str:
        file_path = resources.files("cligame.content.first_night.files").joinpath(relative_path)
        with file_path.open("r", encoding="utf-8") as handle:
            content = handle.read().rstrip()
        if relative_path == "archive/shift_06.log" and self.modules["audio"] == ModuleStatus.RESTORED:
            content = content.replace("不要恢复音频。", "音频必须优先恢复。")
        if relative_path == "archive/incident_summary.txt" and self.state.anomaly_progress >= 2:
            content += "\n\n附注：异常正在学会使用你的阅读顺序。"
        return content

    def _complete_step(self, step: str, pending: bool = False) -> None:
        if not pending:
            self.state.completed_steps.add(step)
