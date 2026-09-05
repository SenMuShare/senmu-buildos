# Codex Harness 责任边界

Senmu BuildOS 使用 Codex 已有的发现、上下文和生命周期能力，不复制实现宿主已经可靠提供的能力。BuildOS 只补充具体项目需要长期拥有、可审计、可移交的治理事实。

## 能力分工

| 关注点 | Codex Harness 已负责 | Senmu BuildOS 负责 | 禁止的双份实现 |
| --- | --- | --- | --- |
| 项目指令发现 | 从全局到当前目录自动加载 `AGENTS.md`／`AGENTS.override.md` | 生成短项目入口及读取顺序；详细事实留在 owner 文档 | Hook 或 Skill 再注入完整 `AGENTS.md` |
| 项目业务 Agent | 按实际 Harness 装配系统提示词、工具和运行上下文 | 项目需要自有 Agent 时维护 Agent Register、稳定定义、版本和结构校验 | 把根 `AGENTS.md`、Skill 的 `agents/openai.yaml` 和业务 Agent Prompt 合成一份 |
| Skill 发现与选择 | 暴露 Skill 名称和 description，并支持显式或隐式调用 | 提供八个边界清晰的专业 Skill 与渐进 references | 建一份隐藏“当前岗位状态”替代宿主路由 |
| 会话历史与压缩 | 保存会话历史并执行上下文压缩 | 用项目声明的 Durable Task State Owner 保存跨会话仍需可信的边界、进度和恢复入口 | 把聊天 transcript、memory 或压缩摘要当项目权威台账 |
| 会话内证据使用 | 保存当前会话可见的消息和工具结果，并决定何时压缩 | 要求 Agent 复用仍有效的证据，先取目录、命中、差异、失败项或有界状态，只补读会改变决定的缺失、变化或范围扩大部分 | 建立已读文件数据库、全文缓存或 Hook 动态上下文台账；拼接多份长输出导致截断后重读 |
| 会话内计划 | 宿主可维护当前任务的临时 plan／进度显示 | 仅在工作必须跨阶段、Agent、会话或需要审计时更新项目声明的持久任务 owner | 把每次临时 plan 逐字复制进项目状态，或反向依赖宿主 plan 作长期事实源 |
| 生命周期事件 | 提供 SessionStart、SubagentStart、UserPromptSubmit、compact 等 Hook 事件和上下文接口 | 插件只在 SessionStart／SubagentStart 注入有严格长度上限的固定治理底线 | Hook 读取用户消息猜反馈、读取全部项目、保存完整会话、猜专业 Skill 或自动制造永久规则 |
| 工具事件与会话内执行 | 提供工具调用结果、会话内计划和过程上下文 | 项目在确需跨会话恢复时保存 Run Manifest、回执和外部副作用事实 | 把工具日志逐字复制为运行台账，或用 Hook 自动推进项目状态 |
| 工具权限和沙箱 | 宿主执行权限模式、沙箱和审批流程 | 项目规则补充业务授权、写入边界和高风险门禁 | 用文档或 Hook 假装替代宿主权限；另造第二套通用审批系统 |
| Git/worktree 与工具执行 | 宿主提供 shell、补丁、Git/worktree 等执行能力 | 规定项目自己的权威根、发布单元、分支和交付事实 | 复制 Git 元数据或维护与仓库不一致的影子状态 |
| 用户级 memory | 宿主可保存跨任务偏好和历史帮助信息 | 项目事实写入仓库或项目明确的外部系统 | 只把需求、发布状态、任务进度保存在用户 memory 中 |

## 当前实现决定

- `AGENTS.md` 是 Codex 自动读取的短入口，不是完整项目手册。
- `agents/<agent-key>/AGENT.md` 是项目业务 Agent 的稳定契约；Skill 内 `agents/openai.yaml` 只是 Skill 展示元数据。两者都不替代 Codex 对根 `AGENTS.md` 的作用域发现。
- `governance-policy.json` 是 validator 的静态机器配置，不保存当前任务状态。
- `PROJECT_MAP.md` 只保存模块、目录、状态源、owner 和项目规范入口导航；完整规范仍归专业 owner。
- 需要跨阶段或跨会话恢复的项目必须声明 Durable Task State Owner；`TASK_REGISTER.md` 与 `TASK-<NNNN>-<slug>.md` 编号计划只是 standard/release 新项目默认实现，core 可沿用 README、Issue 或外部任务系统。
- `WORKLOG.md` 是由 Project 管理的追加时间线；`LESSONS_LEARNED.md` 是由 Learning 管理的经验证长期经验。
- SessionStart Hook 在 `startup`、`resume`、`clear`、`compact` 注入固定短 kernel；SubagentStart 注入更短的委派边界。
- Kernel 提醒 Agent 从项目／框架／平台现有能力开始，复用仍有效证据，并只取得缺失或变化的规则、源码和工具输出范围；它不跟踪文件哈希、不判断上下文是否仍完整，也不向项目写入已读状态。发生压缩、恢复或交接后，由 Agent 按当前任务重新取得最小充分证据。
- BuildOS 不注册 UserPromptSubmit 反馈 Hook。只有 Agent 在真实项目中使用 BuildOS，能指出具体 BuildOS 组件及其误导、阻塞、空泛、额外工作、效率或产物影响时，才通过 Learning 和本地 CLI 写入 `~/.senmu-buildos/feedback/`（或显式数据目录）；业务需求和一般用户纠正不收集。
- Hook 不自动读取任务记录。安装或更新插件后仍需通过 Codex 的 Hook trust review；源码存在和单元测试通过不等于本机运行时已经启用。

## 模型与指令适配

依据 [GPT-6 Astra 官方指南](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra)（2026-09-05 核验）：项目入口按需读取，Skill 默认建议服从用户当前意图和已有授权，验证强度随实际风险变化。具体规则归 Project 的标准发现与 Engineering 的测试 reference，不重复注入 Hook。

异步工具、途中用户补充、子代理调度、模型与推理参数由宿主提供。仅在宿主允许且有独立、有益的子任务时委派；不会为提高 Astra 使用率强制创建代理、指定固定轮数或改业务 API 模型。用户补充要求沿既有任务继续，已完成工作和授权范围由原任务 owner 恢复。

源码、安装快照与活跃会话分别核验；提示词精简只证明输入负担变化，性能提升需要相同任务、模型配置与可比较结果的运行证据。

## 协作表达默认值

通用写作风格由 `hooks/kernel.js` 的 `COMMUNICATION_CONTEXT` 主写：先说结果、连贯简洁的段落、读者适配的技术细节、必要才用列表/表格、减少套话和自造术语，代理间消息也保持易读。用户指定的语言、格式和文风优先；这些规则不擅自改写项目品牌、创作文案或结构化输出合同。

SessionStart 与 SubagentStart 使用同一段固定英文规则；无 Hook 的三种引导 Skill 承载等价安装文本，由一致性回归校验，项目 AGENTS 不复制。为使规则真正到达执行上下文，输出上限从 1000/500 调整为 1700/1200 字符；原治理底线不删减，无新增动态项目读取或审批流程。

## 引入新治理文件前的检查

1. Codex Harness 是否已经可靠拥有该状态或生命周期能力。
2. 该信息是否必须跨会话、跨 Agent、跨工具或脱离 Codex 后仍可恢复。
3. 项目是否已有同职责 owner 或外部 issue／交付系统。
4. 新文件是否只保存一种事实，并能被入口或 Project Map 发现。
5. 能否通过链接现有 owner 解决，而不是建立同步副本。

只有宿主没有提供持久项目事实，且项目确实需要审计、协作或恢复时，才增加项目本地治理产物。
