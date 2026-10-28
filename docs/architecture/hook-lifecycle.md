# Hooks 生命周期设计

## 目标

Hooks 解决长会话、恢复、上下文压缩和子 Agent 启动后短治理边界丢失的问题。它们不读取用户消息来猜反馈，不承载专业知识库，不自动读取整个项目，也不替代确定性门禁或人工治理判断。

Hook 注入跨任务的短边界，Skill 提供按当前结果选择的专业方法。规则正文分别由 Kernel 和专业 owner 维护；Hook 不猜测或保存当前专业角色。

## SessionStart

在宿主支持的 startup、resume、clear、compact 场景注入固定短通用底线：项目事实优先、范围和风险校准、现有能力优先、有效证据复用、有界取得规则／源码／输出、源头治理、必要高风险门禁、可恢复执行、验证与真实完成状态。

固定协作表达默认值同时进入主代理与子代理上下文：清晰直接、自然段优先、减少套话、服从用户指定格式。它不替代项目内容风格；规则 owner 与适配关系见 `codex-harness-boundary.md`。

插件使用 Codex 原生 `PLUGIN_ROOT` 定位脚本，并通过 `additionalContextLimit` 与脚本内字符预算双重限制输出。Codex 已自动发现 `AGENTS.md`，因此 Hook 不读取或复制其正文。

## SubagentStart

向子 Agent 注入更短的委派边界：不得扩大任务、不得越过项目权威和授权、优先复用现有能力与证据、有界取得缺失信息、返回证据与未完成项、不得绕过高风险门禁。

## Agent 后台提交

Agent 在真实项目中使用 BuildOS，发现某个 Skill、reference、模板、脚本、Hook 或规则造成误导、难以执行、内容空泛、额外工作、低效率或差产物时，才通过 Learning 路由使用 `feedback-cli.js submit --component ... --impact ... --quiet` 写入 BuildOS 收纳箱。普通用户需求、业务 Bug 和产品方案调整不收集。正常答复不显示内部标记、候选 ID 或收集回执；CLI 不可用时不冒充已保存。

## 失败策略

- Hook 输出失败不得阻塞普通会话启动。
- Hook 失败时应尽量提供可见状态，不静默伪装为已注入。
- 安全、生产数据、权限、支付、发布完整性和破坏性操作不得只依赖 Hook；项目脚本和 validator 才是可执行门禁。
- 反馈 CLI 失败时不得阻塞正常对话；失败不等于候选已保存，集中审议时以 BuildOS 收纳箱为准。
- 安装或更新插件后，Codex 仍要求用户 review and trust 当前 Hook 定义；源码测试通过不代表本机插件运行时已经启用。

## 当前实现限制

- 不保存完整会话、工具日志或 transcript 正文，只保存不超过 800 字符且经脱敏的触发片段和来源指针。
- 不自动统计、聚类、复盘、生成规则或修改 Skill。
- 不维护隐藏的全局项目事实。
- 不根据目录猜测并自动加载某个专业 Skill。
- 不注入 `SKILL.md` 全文。
- 不维护已读文件、内容哈希或全文缓存；上下文是否保留和何时压缩仍由 Harness 决定。

## 当前专业 Skill 如何选择

当前实现不让 Hook 猜岗位。Codex 根据用户当前请求和八个 Skill 的 description 选择主 Skill：

```text
项目初始化／目录／整体治理  → project
需求／PRD／路线图／迭代     → product
视觉／设计系统／交互／动效   → design
Harness／Agent／物料／流程   → workflow
架构／编码／测试／重构       → engineering
Git／版本／部署／发布        → delivery
POC／证据审计／争议核验      → assurance
复盘／经验沉淀／经验库维护    → learning
```

一个任务只先确定一个主 Skill；只有任务真的跨越职责边界时才组合第二个。Agent 发现 BuildOS 使用问题时按需读取 Learning 的反馈规范并由后台 CLI 收集，不改变当前任务主责。只有用户明确要求集中处理反馈、复盘或治理经验时，才由 Learning 完成查重、证据核对和晋级判断。
