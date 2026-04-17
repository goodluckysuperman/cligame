from __future__ import annotations

from .models import ModuleDefinition, ModuleStatus, ProtocolDefinition, RelayMessage, TaskDefinition

MODULES: dict[str, ModuleDefinition] = {
    "audio": ModuleDefinition(
        key="audio",
        label="音频",
        initial_status=ModuleStatus.OFFLINE,
        restore_minutes=5,
        isolate_minutes=4,
        restore_summary="你恢复了音频模块，残留信号重新获得了广播能力。",
        isolate_summary="你切断了音频模块，低频信号消失了，但也失去了最直接的线索。",
    ),
    "camera": ModuleDefinition(
        key="camera",
        label="监控",
        initial_status=ModuleStatus.OFFLINE,
        restore_minutes=5,
        isolate_minutes=4,
        restore_summary="你恢复了监控模块，Chamber-0 的实时画面重新上线。",
        isolate_summary="你切断了监控模块，避免被反向观测，但失去了视觉证据。",
    ),
    "archive": ModuleDefinition(
        key="archive",
        label="档案",
        initial_status=ModuleStatus.CORRUPTED,
        restore_minutes=4,
        isolate_minutes=3,
        restore_summary="你修复了档案索引，更多事故记录变得可读。",
        isolate_summary="你将档案库锁定为只读快照，安全性提高，但深层记录不再开放。",
    ),
    "lock": ModuleDefinition(
        key="lock",
        label="门禁",
        initial_status=ModuleStatus.DEGRADED,
        restore_minutes=4,
        isolate_minutes=4,
        restore_summary="你恢复了门禁链路，更多门限协议开始被系统识别。",
        isolate_summary="你切断了门禁链路，设施更稳，但某些高级收容路线将关闭。",
    ),
    "auth": ModuleDefinition(
        key="auth",
        label="权限",
        initial_status=ModuleStatus.RESTRICTED,
        restore_minutes=5,
        isolate_minutes=4,
        restore_summary="你恢复了权限校验，系统开始把你写入当前事故配置。",
        isolate_summary="你压低了权限层回响，系统对你的绑定被暂时延缓。",
    ),
}

TASKS: dict[str, TaskDefinition] = {
    "baseline": TaskDefinition(
        key="baseline",
        title="主任务 01：建立事故基线",
        summary="先确认事故范围，再建立可信证据链。",
        steps=(
            "查看事故总览",
            "查看模块状态",
            "读取事故摘要",
            "确认操作者身份",
            "保存第一份离线记录",
        ),
    ),
    "trust": TaskDefinition(
        key="trust",
        title="主任务 02：确认谁在诱导你",
        summary="前辈、日志、远程支援开始出现冲突。",
        steps=(
            "查看远程通讯",
            "决定先信谁",
            "选择第一个处理模块",
            "观察系统如何改变",
        ),
    ),
    "protocol": TaskDefinition(
        key="protocol",
        title="主任务 03：执行收容方案",
        summary="在 04:00 前决定最终协议。",
        steps=(
            "确认至少两项模块状态",
            "检查绑定状态",
            "阅读可执行协议",
            "执行一项收容方案",
        ),
    ),
}

SENIOR_MESSAGES = {
    0: "听我说，别乱碰恢复命令。04:00 前你必须做出一项收容决策，但现在最重要的是建立证据链。先输入 status。",
    1: "很好。先知道事故全貌，再去判断该修什么。下一步输入 modules。",
    2: "现在去档案区。输入 ls /archive，然后打开事故摘要。你得先知道这场事故到底怎么开始的。",
    3: "读完摘要之后，不要急着下结论。再查一次你自己是谁，然后把当前状态保存下来。今晚最先坏掉的不是机器，是信息。",
    4: "接下来就不是我替你做决定了。你会收到远程消息。从那一刻开始，你得自己判断该信谁。",
    5: "记住，恢复模块不只是修系统。每修一处，异常和你自己的身份都会一起变化。",
    6: "时间已经不多了。你现在做的每一步，都在决定最后还能执行哪条协议。",
}

RELAY_MESSAGES: list[RelayMessage] = [
    RelayMessage(sender="远程支援", time_label="03:22", body="你是新接手的吗？先恢复音频。你得知道它在说什么。"),
    RelayMessage(sender="远程支援", time_label="03:29", body="上一班留下的日志只会让你变保守。真正有价值的线索在恢复后的模块里。"),
    RelayMessage(sender="设施广播", time_label="03:34", body="若操作者完成身份确认，高阶协议将开放。请谨慎恢复 AUTH。"),
]

PROTOCOLS: dict[str, ProtocolDefinition] = {
    "minimum_lockdown": ProtocolDefinition(
        key="minimum_lockdown",
        label="最低封锁",
        summary="以最小代价延缓同步，但无法真正解决问题。",
        requirement_text="默认可用，但会留下后患。",
        ending_text="你在最后时刻降下最低封锁。同步被拖慢了，设施暂时安静下来，可你知道这不是结束，只是把灾难推迟给下一班值守者。",
        cost_text="你保住了自己，但放弃了彻底解决问题的机会。",
    ),
    "identity_cutoff": ProtocolDefinition(
        key="identity_cutoff",
        label="身份切断",
        summary="切断你与系统的绑定，让门失去锚点。",
        requirement_text="需要接触 auth 线索，且未被过深绑定。",
        ending_text="你删掉了属于自己的认证链。终端里关于你的记录一条条熄灭，系统再也无法拿你做门。同步停了，可从那一刻起，你也成了系统外的人。",
        cost_text="你活了下来，但世界再也无法正确登记你。",
    ),
    "forced_purge": ProtocolDefinition(
        key="forced_purge",
        label="强制清除",
        summary="用粗暴方式切断异常和所有相关记录。",
        requirement_text="需要更激进的处理轨迹。",
        ending_text="你启动了强制清除。屏幕上的字一行行被擦去，连同你的记录、你的名字、你的痕迹。异常没有继续同步，但你也不知道被清掉的到底是谁。",
        cost_text="你赌上自己的完整性换一个更干净的表面。",
    ),
    "threshold_reset": ProtocolDefinition(
        key="threshold_reset",
        label="门限重置",
        summary="重新定义门与门限，让同步对象失去原本的通路。",
        requirement_text="需要门禁与权限都被重新接入。",
        ending_text="你完成了门限重置。设施没有崩，门也没有开，只是系统把新的门写成了你。同步没有发生，因为你亲手把自己留在了那道阈值上。",
        cost_text="你阻止了更坏的结果，但从此成为门限的一部分。",
    ),
}
