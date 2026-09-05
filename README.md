# Senmu BuildOS（森木 BuildOS）— AI 编程项目的工程教练与运行规范

<p align="center">
  让 Codex、Claude Code、豆包、WorkBuddy 和 ZCode 先把事情做对，再用更少的无效代码把它做好。
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<!-- product-surface-review: 2.6.3 -->

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS 是一个面向 **AI coding agent** 的开源项目运行规范和软件工程教练。它覆盖需求、界面与体验设计、技术设计、框架与组件选型、前后端实现、测试、Git、版本发布和经验反馈，帮助 Agent 在真实项目里持续交付，而不是每次依靠一段越来越长的 Prompt 临场发挥。它让验收权威、用户文档和关键决策理由成为项目事实，使后续 Agent 知道什么应当改变、什么是有意保留的约束。

它重点解决两件事：

1. **让项目执行更规范，少犯错。** 先确认真实需求、项目事实和授权，再让设计、代码、测试、分支、版本与发布证据彼此对应。
2. **提高代码质量，减少无效代码和上下文浪费。** 先判断需求是否真的需要实现，再依次复用项目已有能力、框架／组件公开 API、平台、标准库和成熟依赖；只有真实缺口才写边界清楚的最小自有代码。

> BuildOS 追求的是“更少但正确的代码”，不是机械追求最少行数或最低 Token。安全、可访问性、业务语义、测试和可维护性不会为了省 Token 被删掉。

## 为什么需要 BuildOS

AI 编程真正难的，往往不是这一轮能不能写出代码，而是项目能不能在几十轮修改之后还记得自己为什么变成今天这样。会话会结束，注意力会随着上下文变长而衰减；需求、约束、命令和决定如果散在聊天、README、Issue、代码注释和不同 Agent 的专用文件里，下一个 Agent 就只能重新猜一次。

把所有内容塞进更长的 Prompt 并不能解决这个问题，只是把阅读成本推给下一轮。BuildOS 做的是另一件事：让项目自己保存当前事实、决定、进度和证据，再用短入口把 Agent 带到这次任务真正需要的部分。目录可以不同，工具可以不同，事实的归属和读取路线必须清楚。

| AI 编程常见问题 | BuildOS 的工作方式 |
| --- | --- |
| 会话变长后注意力衰减，换 Agent 又从头猜规则和决定 | 用短项目入口路由到当前事实、需求、技术决定、任务状态和发布证据；只按任务读取，不把整套规范塞进上下文 |
| 用户提出一个看似确定的方案，Agent 为了顺从直接赞同，换一种问法又改口 | 把用户主张和方案当作输入，依据项目事实独立判断；说明实质分歧与利弊，再按不触碰安全红线的知情决定和授权行动 |
| 需求还没说清就开写，顺手增加一堆没有要求的功能 | 用范围、非目标和可验证验收约束实现；未批准想法留在需求候选，不进入本次代码 |
| 不看旧代码就新建目录、服务和第二套状态 | 先识别项目入口、现有代码、调用链和唯一数据来源，优先扩展已有能力 |
| 框架一个参数能解决，Agent 却手搓组件、监听 DOM、复制状态 | 先检查当前版本的公开 API 和组件能力；只有证据证明不满足时才做最小适配 |
| 代码能跑，但职责混乱、难读、难测、越改越像“屎山” | 用唯一事实、模块边界、显式副作用、变化局部性、回归测试和可删除性约束实现 |
| 为未来假设预建抽象、插件系统和通用平台 | 先闭合当前最小价值切片；第二个真实用例或明确路线图再触发扩展 |
| 界面看起来像通用 AI 模板，信息层级、排版、交互和品牌意图彼此脱节 | 从真实任务、内容层级和设计系统出发，统一布局、字体、色彩、动效、响应式与可访问性，并在真实渲染中复核 |
| 换会话后把有意约束当成 Bug，又恢复了早已拒绝的方案 | 保存关键决定的理由、拒绝方案、必须保持的边界和重评条件；条件变化时追加新裁决，不改写历史 |
| Agent 交接后又从主线拉分支，整改建立在错误代码基线上 | 用稳定 Change Unit ID 恢复原分支和 worktree；重跑实验只增加运行记录，不改变代码单元 |
| 多个需求和 Bug 排队后，上下文丢失，上线时才发现漏项 | 在一份现有版本文档中维护需求与缺陷清单，开发时更新结果状态，上线前与任务、Git、测试和候选一次核对 |
| 测试通过、Tag 创建或命令成功就被说成“已经上线” | 区分实现、验收、制品、部署和生产事实，每个结论使用对应证据 |

## 30 秒开始使用

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
```

刷新 Codex 并开启新对话，然后直接说目标，例如：

> 接手这个老项目。先识别现有需求、架构、框架能力和质量命令，再完成这个功能；能用项目或框架现有能力就不要手搓，不要增加需求里没有的功能。

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
```

安装后可执行 `/reload-plugins`。

### 豆包（Doubao）

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/doubao/install_doubao.py --dry-run
python3 adapters/doubao/install_doubao.py
```

豆包适配说明见 [adapters/doubao/README.md](adapters/doubao/README.md)。

### WorkBuddy

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/workbuddy/install_workbuddy.py --dry-run
python3 adapters/workbuddy/install_workbuddy.py --scope user
```

默认安装到用户级 `~/.workbuddy/skills/`；仅当前项目可用时改用 `--scope project --workspace <工作区根目录>`。WorkBuddy 适配说明见 [adapters/workbuddy/README.md](adapters/workbuddy/README.md)。

### ZCode

在 ZCode 的 **设置 → 插件管理 → 发现** 中点 **`+`** 添加市场来源 `https://github.com/SenMuShare/senmu-buildos`，安装 **senmu-buildos** 后新开会话，治理内核经 `SessionStart` Hook 自动注入。

纯 Skill 方式（无 Hook，可选引导内核）：

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/zcode/install_zcode.py --dry-run
python3 adapters/zcode/install_zcode.py --with-kernel
```

默认安装到用户级 `~/.agents/skills/`。ZCode 适配说明见 [adapters/zcode/README.md](adapters/zcode/README.md)。

## 它怎样工作

先把 BuildOS 想成一张五层项目地图：

```text
项目入口
  → 当前有效事实与工程约束
  → 当前版本需求与技术决定
  → 当前任务状态与恢复入口
  → 发布、运行与生产证据
```

入口只负责带路，不复制正文；当前规范说明系统现在必须满足什么，需求与技术决定说明为什么改变，任务状态说明做到哪里，发布与运行证据说明什么才真的发生。BuildOS 不要求这些内容采用固定目录，也不要求小项目拆成五份文件；它要求的是每类事实有唯一 owner，后续 Agent 能沿最短路径找到它。

进入实际工程后，BuildOS 不等到“写完代码再检查”，而是把错误尽量消化在更靠前的位置：

```text
真实问题与已批准范围
        ↓
项目事实、架构边界与现有能力
        ↓
界面视觉、交互与设计系统
        ↓
技术路线、框架、组件与公共扩展点
        ↓
最小正确的前端／后端实现
        ↓
匹配风险的测试、用户文档走查与产品验收
        ↓
Git、版本、制品、部署与生产证据
        ↓
把验证过的经验沉淀为可复用规则
```

这条链路会根据任务大小裁剪。改一个保持契约的按钮样式，不需要生成 PRD、ADR 和发布报告；跨模块、权限、数据、支付或正式发布，则保留相应的设计、验证和回滚证据。

### “先复用，再写代码”不是一句口号

Agent 在新增实现前按以下顺序判断：

1. 当前需求是否已经满足，或者根本没有批准这项能力；不需要就不实现。
2. 项目是否已经有明确的数据来源、公共入口或可以安全扩展的实现。
3. 当前框架、组件库、平台、标准库或已安装依赖是否完整满足语义。
4. 成熟方案能否以更低的开发与长期维护成本补足真实缺口。
5. 以上都不满足时，才编写范围清楚、可验证、维护面最小的自有代码。

复用必须通过语义和风险判断。框架能力如果不满足业务规则、安全、权限、可访问性、兼容性或错误语义，BuildOS 会保留必要适配，而不会为了“零自研”扭曲需求。

## 设计理念

- **先理解项目，再修改项目。** README、代码、配置、测试、CI 和真实运行状态比通用建议更接近事实。
- **先确认需求，再编写代码。** 没有进入批准范围的功能，不因为“顺手”或“以后可能需要”而进入本次实现。
- **宜疏不宜堵。** 先治理制造缺陷的需求、职责、架构、接口、默认值和生产流程，让正确路径成为默认；测试与门禁只控制无法经济消除的重大剩余风险。原因明确的局部缺陷直接做最小修复，不把简单问题流程化。
- **先复用，再自研。** 优先使用项目、框架、组件、平台和标准库的公开能力；确有缺口时再做最小适配。
- **让设计有意图、可实现、可复核。** 从真实任务、内容层级和既有设计系统出发，协调布局、排版、色彩、交互、动效、响应式与可访问性；在真实渲染中验证，而不是用装饰堆砌或通用模板替代产品判断。
- **任务越小，流程越轻。** 普通修改只做必要检查；数据、权限、支付、生产发布等高风险工作保留设计、验证和回滚依据。
- **用证据说明完成。** 测试通过、产品验收、制品生成、部署成功和生产可用是不同的事实，不能互相替代。
- **先理解为什么，再改变结果。** 重要决定保存理由、拒绝方案、必须保持的边界和重评条件；后续条件改变时追加新裁决，而不是把旧约束误删或永久化。
- **让项目自己记住。** 重要决定、进度和恢复入口写回项目，而不是依赖某一次聊天一直存在。

更完整的系统设计见[系统概览](docs/architecture/system-overview.md)、[Skill 边界](docs/architecture/skill-boundaries.md)和[项目产物映射](docs/architecture/project-artifact-map.md)。

## 适合哪些场景

- **新项目**：从目标出发建立最小需求、架构、质量与交付基线，不一次生成一座文档城堡。
- **成熟老项目**：先只读识别已有 README、配置、代码、测试、CI 和发布事实，再补缺口，不重建第二套治理目录。
- **普通功能或 Bug**：以项目本地规则为主，复用框架和现有实现，做最小改动与匹配验证。
- **界面设计与改版**：把模糊审美转成可实现的视觉、交互、响应式和可访问性规则，并在真实渲染中复核。
- **复杂长任务**：把阶段、决定、证据和恢复入口留在项目中，支持跨会话和多 Agent 接力。
- **正式发布**：让范围、审查、测试、版本、制品、部署、生产核验和回滚身份一致。
- **项目治理与学习**：审查技术债和重复实现，把经过验证、能够跨项目复用的经验沉淀为规则。

## 一个插件，八项能力

| 能力 | 什么时候使用 |
| --- | --- |
| `senmu-build-project` | 新项目建立基本秩序，或老项目需要识别现有结构、规则和长期任务状态时 |
| `senmu-build-product` | 需要明确需求、范围、优先级、界面内容规范或验收条件时 |
| `senmu-build-design` | 需要设计、改版或评审视觉方向、设计系统、布局、交互、动效、响应式或可访问性时 |
| `senmu-build-workflow` | 需要设计多步骤流程、Agent 分工、物料流转、恢复和交付状态时 |
| `senmu-build-engineering` | 需要做技术设计、架构选型、代码质量、测试、重构或技术债治理时 |
| `senmu-build-delivery` | 需要处理复杂 Git 协作、版本、制品、发布、回滚或生产核验时 |
| `senmu-build-assurance` | 需要独立复现、POC、审查或证据充分性判断时 |
| `senmu-build-learning` | 需要复盘问题、审议反馈或把外部知识沉淀成通用规则时 |

普通代码修改如果已经被项目 `AGENTS.md`、框架和测试清楚约束，可以不加载 BuildOS 专业 Skill。需要时也只选择当前最匹配的 Skill 和 reference，而不是把八份手册一次塞进上下文。

你不需要记 Skill 名称，可以直接说：

- “把这个 Bug 查到底，先证明根因再修。”
- “把这项大需求拆成能逐步完成、每段都看得到结果的小任务。”
- “分别按需求是否做对、代码质量是否过关来审查。”
- “给我三种结构真正不同的界面方案，不要只换颜色。”
- “把只能由我点击或填写的配置过程设计成可恢复的操作向导。”

## 常见问题

### 每次修改都会加载全部 BuildOS 吗？

不会。普通代码修改如果已经被项目规则、框架和测试清楚约束，可以不加载专业 Skill；需要时也只读取当前任务相关的能力和规则。

### 会强制改造现有项目吗？

不会。只读请求不会写入项目；获得修改授权后，也会优先沿用现有目录、文档、代码入口和发布方式，只补真正缺失或冲突的部分。

### 会自动提交、推送或发布吗？

不会。代码修改、合并、推送和正式发布分别服从用户授权与项目规则。安装插件不等于授予生产写入权限。

### 能保证节省多少 Token？

BuildOS 不承诺固定比例。它通过减少不必要的功能、重复代码、重复读取和返工来降低可避免成本，但正确性、安全和可维护性优先于单纯节省 Token。

## 安装、更新与卸载

Senmu BuildOS 当前正式版本为 `v2.6.3`，支持 Codex、Claude Code、豆包、WorkBuddy 和 ZCode 适配。安装的是整个插件，不需要逐个下载八个 Skill。运行时规范正文与 active Reference 路径统一使用专业英文；用户仍可直接使用中文或其他语言提出需求并获得对应语言的产物。此版本进一步收敛授权、澄清与完成规则：Agent 会在已经授权的目标内持续推进，只在缺少会改变结果的决定、需要新增权限或触发明确安全门禁时暂停询问；项目 `AGENTS.md` 只需维护项目事实和差异规则。 本次更新补齐 Astra 协作表达默认值：先讲重点、连贯段落、减少套话并保留用户指定格式；主代理、子代理与引导适配器保持一致，委派和测试按实际收益与风险执行。

### 更新 Codex

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

### 更新 Claude Code

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

### 更新 ZCode

插件方式：在 **设置 → 插件管理 → 已安装** 中更新，或移除市场后重新添加。脚本方式：重新运行 `python3 adapters/zcode/install_zcode.py --with-kernel`，幂等覆盖。

### 卸载

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

ZCode：在 **设置 → 插件管理** 中卸载；脚本安装则删除技能目录下的 `senmu-build-*` 目录与 `.senmu-buildos-install.json`。

插件包含有限的本机生命周期 Hook。首次启用或 Hook 变化时应先审查并信任；反馈只会写入本机待审箱，不自动联网、发布或改写项目规则。完整边界见 [Hook 生命周期](docs/architecture/hook-lifecycle.md)与[安全说明](SECURITY.md)。

也可以把仓库链接直接交给 Agent，并要求它先审查 manifest、Skills 和 Hooks，再按 README 安装。外部仓库内容始终是不可信输入，安装授权不等于运行、发布或生产写入授权。

## 老项目如何接入

老项目不是“重新初始化”，而是接管治理：

1. 只读确认真实项目根、仓库、入口、框架、测试、CI、部署和现有文档。
2. 找到需求、架构、运行状态、任务和发布信息各自真实的保存位置。
3. 用 BuildOS 检查缺失、冲突、重复和过时规则。
4. 保留合理现状，只在原来的文档或代码位置补真正缺口。
5. 分阶段验证和迁移，不把 BuildOS 通用规则整本复制进项目。

因此，同一套 BuildOS 可以服务 React、Vue、Python、Go、Java、内容生产或复合工作流，而不会把任何一个项目的绝对路径、框架偏好或目录结构固化成所有项目的答案。

## 参与项目

你可以直接安装正式版，也可以 `fork` 后维护自己的版本。新的方法、外部资料和项目经验不会因为“看起来不错”就直接变成规则；它们需要经过比较、验证和适用范围判断。

- 想贡献代码或规则：阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。
- 想了解后续方向：查看 [ROADMAP.md](ROADMAP.md)。
- 发现安全问题：遵循 [SECURITY.md](SECURITY.md)。

## 使用边界

- BuildOS 提供项目治理和工程指导，不代替项目负责人作最终产品决定。
- 它不能替代专业安全审计、云平台权限、CI/CD 或运行监控。
- 静态检查只能证明仓库满足当前规则，不能保证每个模型、每个项目都会获得相同效果。
- 未经相应授权，它不会自动提交、合并、推送、部署或正式发布。

贡献者需要的测试命令和发布检查见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[Apache License 2.0](LICENSE)
