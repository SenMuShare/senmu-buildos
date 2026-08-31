# Senmu BuildOS 系统架构

## 产品模型

Senmu BuildOS 采用“一个插件、八个平级专业 Skill、插件级短通用底线、确定性工具和行为测试”的结构。专业 Skill 按当前任务职责加载，不按组织部门或现有 reference 数量机械拆分。BuildOS 是通用治理系统，每个项目通过选择、映射和演进形成自己的 Project Governance Instance。

## 源码项目、插件包与运行入口

Senmu BuildOS 有一个内部权威 Git 库和一个白名单生成的公开 Git 投影。权威库保存完整源码、项目任务、工作日志和私有验证证据；公开投影只保存用户安装、理解和验证产品所需的源码面。`.codex-plugin/`、全部 Skills、Hooks、公开文档、脚本和测试共同构成一个统一版本的发布单元。Codex 安装后看到的八个 Skill 不是八个独立发布项目；安装或缓存目录也不是源码权威。

因此，通用经验反哺以 BuildOS 仓库根为变更边界：先做整仓影响分析，再修改正确 owner。最终即使只改一份 Markdown，也要确认相邻 Skill、路由、模板、Hook、脚本、测试和发布信息是否受影响。应用项目、BuildOS 源码修改、候选安装和公开发布分别拥有独立 Git／状态／授权，不能互相代替。

## 源码项目的自举治理

BuildOS 源码工作区是 `publication-workspace`：内部权威库是治理实例，公开库是可重建的发布投影。它使用 Project 管理权威根、owner、持久任务状态和发布单元；使用 Engineering 治理 Skill、Hook、adapter、脚本、测试和架构文档；使用 Delivery 收口版本、commit、Tag、公开投影和 GitHub Release。其他专业 Skill 仍按当前交付物加载，不组成固定流水线。

自举实例映射既有 owner：`skills/`、`hooks/`、`adapters/`、`docs/architecture/`、`scripts/`、`tests/`、`VERSION`、`CHANGELOG.md` 和 Release workflow 继续保存专业事实。`governance/` 只在内部权威库保存短项目地图、跨阶段任务状态和工作日志，不建立平行 `product/`、`engineering/` 或 `delivery/` 正文。内部治理校验和公开产品面校验独立执行；公开包校验不反向依赖未发布的任务、日志或审查记录。

## 事实权威与治理标准

1. 用户当前明确要求决定目标、授权和禁止边界。
2. 具体项目的真实目录、运行状态、项目入口、policy、schema、台账和发布证据是当前事实权威。
3. 当前任务匹配的 Senmu BuildOS 专业 Skill 提供治理标准，用于发现并改善缺失、冲突、重复、过时或不可搬迁的 owner。
4. 通用示例和默认目录只在项目尚无适用实现时作为候选。

Senmu BuildOS 不替代具体项目的事实源，也不把“已有”误判为“合理”。已有项目先只读审视；获得授权后治理原 owner，不建立第二套长期事实。

## 任务连续性

需要多个依赖步骤、阶段、Agent 或会话的工作统一登记到项目声明的 Durable Task State Owner。standard/release 新项目默认使用 `governance/tasks/`；core 可沿用 README、Issue 或外部任务系统，成熟项目可以映射任务包、数据库或外部系统。八个专业 Skill 仍分别维护自己的领域事实。当前 Hooks 不自动读取或总结任务状态。

## 从产品意图到 Git 行为

BuildOS 不要求用户设计分支机制。用户可以用产品语言说“继续当前版本”“开一条长期继任线”“把这批收进主线”“先不要发布”或“发布”。Delivery 结合项目事实，把它们翻译成版本线、Change Unit、任务分支、worktree、接收矩阵、候选和有限发布会话。

静态机制由项目 policy 持有：当前主线是 `release_ready` 还是 `integration`、是否禁止直接写主线、worktree 根、Change Unit 状态集、正式 Tag 语义和授权模式。动态事实仍回到原 owner：任务边界与产品决定在 Durable Task State Owner，分支与 commit 在 Git，部署与发布在运行端和 Release Record。待接收状态从已封口 Change Unit 与 Git 可达性派生，不建第二本全局分支账。

## 组织学习飞轮

反馈飞轮分为两个阶段：Agent 在真实项目中使用 BuildOS，发现 BuildOS 组件造成误导、难以执行、空泛、额外工作、低效率或差产物时，通过 Learning 和本机 CLI 主动提交；用户再按需触发 Learning 集中审议。用户消息不会被 Hook 自动抓取，业务需求和项目 Bug 不进入 BuildOS 收纳箱。单条反馈不是规则，收纳箱不是事实 owner，任何反哺仍需人工授权和正常工程流程。

默认反馈箱位于 `~/.senmu-buildos/feedback/`，也可通过 `SENMU_BUILDOS_DATA_DIR` 显式改址。它不写入业务项目、不联网、不保存完整会话，不承担看板或统计职能。

## 核心治理顺序

BuildOS 先确认用户目标和项目事实，再选择能形成端到端价值闭环的最小任务切片；实现时先搜索现有 owner、代码、平台能力、依赖和成熟方案，只有真实缺口才新增能力。质量首先内建到需求、职责、架构、接口、数据、默认值和流程，测试与门禁只控制无法消除的重大剩余风险。最终以项目本地状态、验证、交付证据和恢复路径收口，而不是以文档数量、工具成功或代码行数证明完成。

当用户请求建议、判定或治理审视时，BuildOS 以工程教练模式输出：先分离已核对事实和盲区，再识别当前场景与专业 owner，给出风险匹配的首选方案、可接受替代、例外和收口条件。这种结构只在复杂或高风险现场展开；普通小任务仍以最小充分建议处理，不强制模板或新台账。

用户是目标、偏好和授权的权威，不自动成为当前系统事实或方案正确性的权威。Product 与 Engineering 在日常讨论中先区分期望状态、项目事实、推断、未知项和建议；可从项目合理核验的现状先查原 owner、实现或运行证据，外部知识会实质改变结论时再查适用的一手资料。证据不支持用户提出的方案时应直接说明，证据不足时给条件性结论；Assurance 只在独立、争议或正式审查需要时介入。

正式发布的收口横跨但不混并多个 owner：Delivery 在生产验证后串联生产运行端、本机构建端、按需远程制品库和本次 Git 执行面；镜像／制品保留由版本发布 owner 决定，分支／worktree 安全条件由代码管理 owner 决定。默认保留当前已验证版本和一个已验证回滚版本，项目明确策略优先；数据库、Volume、Git 历史、其他项目和全局缓存不进入自动清理。

## 技术关系

```text
Codex 插件 senmu-buildos
├── 生命周期 Hooks
│   ├── SessionStart：恢复短通用底线
│   └── SubagentStart：恢复子 Agent 最小边界
├── 本机反馈 CLI：供 Agent 提交 BuildOS 真实使用问题
└── 平级 Skills
    ├── senmu-build-project
    ├── senmu-build-product
    ├── senmu-build-design
    ├── senmu-build-workflow
    ├── senmu-build-engineering
    ├── senmu-build-delivery
    ├── senmu-build-assurance
    └── senmu-build-learning
```

Hooks 不加载全部 Skill，不替代项目 validator，也不作为高风险操作的唯一门禁。本地 CLI 的反馈写入仅形成待审候选，不自动改变项目事实或 BuildOS 规则，也不向正常用户答复泄露内部标记或候选 ID。

Senmu BuildOS 与 Codex 原生能力的分工见 [Codex Harness 责任边界](codex-harness-boundary.md)。

## 唯一 owner 规则

- 每份 reference、模板和脚本只能有一个运行时 owner。
- 其他 Skill 需要该内容时，通过职责路由或明确链接访问，不复制正文。
- 少量跨领域底线由 Hooks 恢复；完整方法论只存在于唯一专业 owner。
- 真正需要在多个入口重复的安全边界必须保持短小，并在架构文档中说明重复理由。
- 任务状态模型、目录和模板由 `senmu-build-project` 唯一负责；产品行为与界面内容由 `senmu-build-product` 负责，视觉、交互与设计系统由 `senmu-build-design` 负责；Lessons Learned Register 的语义、schema 和生命周期由 `senmu-build-learning` 唯一负责。其他 Skill 只链接自己的专业产物和更新对应阶段。
- 项目 Agent 的定义框架、登记与模板由 `senmu-build-workflow` 唯一负责；Project 初始化器仅在显式 `--with-agents` 时组合这些资源，不复制其内容 owner。

## 当前排除项

- 不在 Hooks 中注入完整专业规则、动态强度模式或基准数据。
- 不创建尚无成熟内容的 `senmu-build-operations` 空 Skill。
- 在正式发行验证完成前，不把源码存在、静态校验或单元测试通过误报为插件已经安装、Hook 已经受信任或运行时行为已经验证。
