# Senmu BuildOS — Agent Skills for Codex & Claude Code

**让想法成为能持续迭代的产品。**

*Understand the goal. Make the right decisions. Carry the work through.*

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

你知道想做什么，却未必知道还需要哪些需求、设计、工程和交付判断。森木 BuildOS 是给 AI 编程助手的一套项目教练方法：从你的目标和项目现状出发，补齐当前需要的专业工作，把决定落到代码、规范和可核对的结果里。

它覆盖产品、UI/UX、工程、项目治理、工作流、交付、核验与学习。新项目建立必要起点，旧项目复用有效能力，小改动直接推进；不同模型和会话通过同一套项目事实继续协作。

**你说目标，BuildOS 帮 AI 找到下一步该做什么、为什么做、做到什么算完成。**

[![License](https://img.shields.io/github/license/SenMuShare/senmu-buildos)](LICENSE) [![Public release](https://img.shields.io/github/v/release/SenMuShare/senmu-buildos?label=public%20release)](https://github.com/SenMuShare/senmu-buildos/releases/latest)

[快速开始](#quickstart) · [第一次怎么用](#first-use) · [八项能力](#skills) · [常见问题](#faq) · [更新与卸载](#maintenance)

<a id="quickstart"></a>
<a id="30-秒开始使用"></a>
## 快速开始

先准备支持插件的 Codex 或 Claude Code，以及本机可用的 Git 和 Node.js。启用前审阅 [Hooks](hooks/hooks.json) 与[安全说明](SECURITY.md)，只信任你确认过的来源。

### Codex

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

刷新客户端并新开项目对话，核对列表中的来源与版本，再试下面的任务。

### Claude Code

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
claude plugin list
```

新开会话，或在当前会话运行 `/reload-plugins`；在 `/plugin` 的已安装列表确认插件状态。项目指令兼容和排障见 [Claude Code 适配说明](adapters/claude-code/README.md)。

以上命令安装的是**公开市场提供的版本**，不保证与本文的源码版本相同；私有制品遵循对应授权与安装流程。安装成功、当前会话加载和任务实际执行分别确认。命令差异以已安装客户端的 `--help`、[Codex 文档](https://developers.openai.com/codex/cli/reference/)和 [Claude Code 文档](https://code.claude.com/docs/en/discover-plugins)为准。

<details>
<summary>豆包、WorkBuddy、ZCode 与纯 Skill 安装</summary>

这些适配器共用八项专业能力，但纯 Skill 安装不等于完整插件的生命周期 Hook。先取得可信源码，在包含 `skills/` 和 `adapters/` 的产品根目录操作；Python 适配脚本需要 Python 3。以下 clone 命令取自公开仓库。

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
```

| 宿主 | 先预览 | 确认后安装与说明 |
| --- | --- | --- |
| 豆包 | `python3 adapters/doubao/install_doubao.py --dry-run` | `python3 adapters/doubao/install_doubao.py`；[目标目录与卸载](adapters/doubao/README.md) |
| WorkBuddy | `python3 adapters/workbuddy/install_workbuddy.py --dry-run` | `python3 adapters/workbuddy/install_workbuddy.py --scope user`；[项目级安装与卸载](adapters/workbuddy/README.md) |
| ZCode | `python3 adapters/zcode/install_zcode.py --dry-run` | `python3 adapters/zcode/install_zcode.py --with-kernel`；[插件方式与卸载](adapters/zcode/README.md) |

ZCode 也可在插件管理中添加市场 `https://github.com/SenMuShare/senmu-buildos`，安装后新开会话。豆包、WorkBuddy 和 ZCode 的纯 Skill 路径按适配方式提供可命中的引导能力，不承诺每次会话自动注入。不要重复安装多个副本。

</details>

<a id="first-use"></a>
## 第一次怎么用

打开项目，任选一个真实任务。你不需要记住八个 Skill 的名字；下面是输入示例，不是效果保证。

### 1. 接手已有项目，先不改代码

> 先只读了解这个项目，找出运行入口、现有规则和测试命令，说明这个需求可以复用什么，暂时不要改代码。

**检查结果：** 给出真实路径、当前约束、可复用能力和未知项；没有趁机初始化第二套目录或修改项目。

### 2. 把反复出现的 Bug 查清楚

> 把这个 Bug 查到底。先复现原始症状并查明原因，再做最小修复，最后验证原始场景和受影响的回归；无法复现的部分明确说明。

**检查结果：** 区分推测与证据，说明修改位置、实际运行的检查和仍未验证的范围，而不只是说“应该修好了”。

### 3. 在现有项目里增加功能

> 先确认需求范围和完成标准，沿用现有结构与组件，分步实现并验证，不增加未要求的功能。

**检查结果：** 需求与实际改动对应，已有实现得到复用，完成项和待验证项分开说明。

形成或更新需求文档时，每个功能保留目标版本与“需求描述、功能描述、功能逻辑、前端交互描述”；异常必须写清，相关原型／UI 记录采用范围并关联到具体需求。没有设计稿不强制补图，用户明确指定的替代格式优先。详见[需求编写与原型关联](skills/senmu-build-product/references/product-requirements-and-iteration.md#21-per-feature-requirement-contract)。

已有方案需要评审时，可以说“分别按需求是否做对、代码质量是否过关来审查”；需要人工操作第三方控制台时，可以说“把只能由我点击或填写的配置过程设计成可恢复的操作向导”。需要明确点名能力时，从[能力表](#skills)查看其入口。

也可以直接说“帮我做一个浏览器库存系统”“这个页面很乱”或“照这张图实现”。BuildOS 根据目标识别需要的产品、设计与工程工作；只写需求时停留在需求范围。持久 UI 使用 `design/UI_SPECIFICATION.md`，既有有效规则经治理迁移保留，AGENTS.md 与项目地图连接规范、真实组件和走查入口。

<a id="why"></a>
<a id="为什么需要-buildos"></a>
## 我们想改变的，是 AI 推进项目的方式

**把专业判断带到普通需求里。** “帮我做个库存系统”已经包含用户操作、数据口径、界面状态和交付方式等问题。BuildOS 引导 AI 在当前阶段识别这些工作；你可以用业务语言交流，不必先报出 Skill 名称或工程术语。

**让方法适应项目。** 一次性原型、持续运营的产品、纯后端服务和已有大型仓库，需要的工作不同。先判断实际能力和缺口，再选用方法；已有规则覆盖的小改动保持直接。

**从源头减少返工。** 先查现有组件、接口与状态由谁维护，再决定是否新建。Bug 要追到原因，规范冲突要形成采用决定，测试要能验证实际问题。清楚的职责和适量的代码，比越来越长的禁令更有价值。

**让下一位 AI 接得上。** 需求版本、设计依据、任务进度和验证结果留在项目中。换会话或换模型时，从明确的入口继续；实现完成、用户验收、已部署和已发布分别记录。

BuildOS 适合持续建设产品的独立开发者、产品经理和小团队。你继续决定目标与取舍，AI 获得一套组织专业工作的共同方法。

<a id="example"></a>
## 一个可以检查的例子

仓库内的 [Python／TypeScript 质量检查示例](skills/senmu-build-engineering/assets/code-quality/examples/README.md)演示了“规则如何变成可运行检查”，而不是只有一句“请遵守规范”。

以现有 Python 价格计算示例为例：[`total()`](skills/senmu-build-engineering/assets/code-quality/examples/python/sample_app/domain.py)计算扣减后的金额，负结果报错；[`check.py`](skills/senmu-build-engineering/assets/code-quality/examples/python/check.py)把格式、静态规则、类型、依赖边界和业务测试接到同一入口。

```text
正常实现 → 统一检查通过
制造指定违规 → 对应检查失败
恢复实现 → 统一检查重新通过
```

例如，把返回值改成字符串用于验证类型检查，把减法改成加法用于验证业务测试。仅在临时副本中按示例说明运行，保留项目已有工具；这些是可重复的工具案例，不是客户证言，也不证明某个模型的提升幅度。

可选的[接口契约运行示例](skills/senmu-build-engineering/assets/contract-examples/README.md)演示定义／代码声明到生成物、真实调用和业务验证的连接；依赖只用于示例，不强制改变项目技术栈。

<a id="skills"></a>
<a id="一个插件八项能力"></a>
## 八项能力，各自解决一类难题

### Product · 把“大概想要”变成可以验收的需求

一句想法往往没有说清失败、取消、切换和恢复时该怎么办。Product 把目标、范围、业务行为、界面反馈与验收条件连在一起，再把功能放进正确的版本；相关原型也保留明确的采用范围。

你得到的是可实施、可核对的需求，以及本版做什么、暂不做什么的决定。可以直接说：“把批量导出需求讲完整，特别是失败重试和权限。” [查看产品方法](skills/senmu-build-product/SKILL.md)

### Design · 让页面像同一个产品，也让操作走得通

“高级一点”需要变成层级、布局、字体、颜色、密度和状态的具体选择。Design 从真实用户任务与参考出发，区分新界面、存量整改和图稿还原；用页面族、代表样板和真实组件源维持一致性，同时保留有理由的变体。

持续维护的 UI 统一使用 `design/UI_SPECIFICATION.md`，实现连接真实主题、token 和组件。交付按适用范围核对实际画面与操作路径。可以说：“这些页面很乱，帮我找出原因并统一起来。” [查看设计方法](skills/senmu-build-design/SKILL.md)

### Engineering · 复用已有能力，把问题修在源头

先理解入口、调用方、数据与状态，再决定实现。Engineering 处理技术选型、架构、前后端契约、语言规范、排障和代码评审；优先用项目与成熟组件已有的能力，避免为一个局部需求长出一套新框架。

修复要回到原始失败场景，并验证受影响的调用方。你能看到选择理由、具体改动和真实检查结果。可以说：“这个 Bug 总复发，查清根因，沿现有架构修好。” [查看工程方法](skills/senmu-build-engineering/SKILL.md)

### Project · 让新项目有起点，让旧项目有清楚的规则

Project 先识别项目根、已有约束、维护责任和实际能力。新项目生成需要的治理起点；旧项目通过盘点与迁移收敛规范，保留有效决定。AGENTS.md 提供工作原则和导航，专业正文由各领域维护。

你得到能找到、能执行、能继续的项目约定。UI 是否存在、规范由谁维护、下一步在哪里继续，都应有明确答案。可以说：“接手这个项目，先检查哪里缺规范，再把需要的部分整理好。” [查看项目方法](skills/senmu-build-project/SKILL.md)

### Workflow · 把能跑一次的步骤，变成能恢复的流程

多代理、文件处理或外部控制台操作，容易卡在交接和中断。Workflow 明确输入输出、运行身份、阶段状态、人工操作和恢复入口；区分原始资料、中间产物、最终交付和归档，让重试知道该从哪里继续。

它也帮助设计业务 Agent 与提示词。你得到可执行的流程约定和清楚的交接，而不是一句“让几个 Agent 合作”。可以说：“这批任务失败后总要重来，帮我把恢复和交付流程理顺。” [查看工作流方法](skills/senmu-build-workflow/SKILL.md)

### Delivery · 清楚知道交付到了哪一步

代码提交、构建成功、部署完成和生产验证是不同事实。Delivery 连接分支与工作树隔离、并行改动整合、版本制品、发布权限、回退和现场核对；沿项目已经采用的交付入口执行。

你得到明确的候选、检查、实际发布状态和恢复依据。可以说：“把这一批改动整合成一个版本，检查通过后按既有流程发布。” [查看交付方法](skills/senmu-build-delivery/SKILL.md)

### Assurance · 把疑问变成有证据的结论

“这个方案是不是有问题？”需要清楚的对象、版本、范围和判断依据。Assurance 用源码、复现、对照或 POC 检查假设，把事实、推断和未知分开，并说明影响、修复方向和复核条件。

你得到的是可追溯的发现与优先级。独立性取决于真实评审安排，不靠换一个角色名；明确审计与日常自检也按任务区分。可以说：“客观审查这套部署方案，判断问题在哪里。” [查看核验方法](skills/senmu-build-assurance/SKILL.md)

### Learning · 让一次解决的问题，成为下一次可用的经验

每次出错都加一条规则，最后会得到互相冲突的说明。Learning 先核查问题和改进证据，再决定是当前项目修正、项目经验，还是值得进入 BuildOS 的通用方法；外部 Skill 的做法也经过适用性与重复检查。

你得到经过取舍的经验，以及唯一的正式维护位置。可以说：“复盘这次返工，哪些只适合本项目，哪些应该改进通用方法？” [查看学习方法](skills/senmu-build-learning/SKILL.md)

八项能力平级、按需取用，任务可以只需要其中一项。Python、TypeScript、Go、Java、Rust 等专业规范由 Engineering 按需读取。运行时方法采用英文，你可以用中文、英文、日文或其他语言协作。

<a id="how-it-works"></a>
<a id="它怎样工作"></a>
## 怎样与现有项目协作

**接口协作按实际边界组织。** 全栈、多个全栈或前后端分工都可以按完整功能推进；先找到当前契约、调用方和验证入口，再决定实现顺序。初始化与授权治理会校准唯一维护源及导航，日常工作直接复用；纯前端局部修改不强制创建 HTTP 文档。详见[接口契约指导](skills/senmu-build-engineering/references/api-and-boundary-contract-governance.md)。

会话会结束，注意力会随着上下文变长而衰减。BuildOS 的做法是让项目保存可恢复的事实，而不是不断加长提示词。

```text
项目入口
  → 当前事实与工程约束
  → 需求和设计决定
  → 任务进度与恢复点
  → 发布、运行与生产证据
```

这些是需要连续保存的事实，记录规模随任务调整。任务进度可以沿用 Issue 或既有任务记录；持久 UI 的当前规范统一进入 `design/UI_SPECIFICATION.md`。已有有效决定通过治理迁移保留，项目入口与质量命令继续连接实际实现。

**宜疏不宜堵。** 优先修正制造错误的需求、职责、接口或默认流程，测试与门禁控制重大剩余风险；原因清楚的小问题直接做最小修复。复用也不能以牺牲业务语义、安全、权限或兼容性为代价。

工作过程按需求理解、设计、实现、验证和交付衔接，任务越小，流程越轻。详细方法见[系统概览](docs/architecture/system-overview.md)、[Skill 边界](docs/architecture/skill-boundaries.md)和[项目产物映射](docs/architecture/project-artifact-map.md)。

<a id="faq"></a>
<a id="常见问题"></a>
## 常见问题

**每次都加载整套规范吗？** 不需要。已被项目规则和测试覆盖的普通修改，可以不调用专业 Skill；需要时才读取相关参考。实际加载取决于客户端与任务，不能仅凭文件存在判断生效。

**会自动改造项目、提交或发布吗？** 安装不授予这些权限。读取、修改、提交、推送和生产操作遵循用户授权与项目规则；只读请求保持只读，已批准的工作也不应被重复审批打断。

**只是另一份 AGENTS.md 吗？** 不是。AGENTS.md 保存项目常用原则与导航，Skill 提供当前任务需要的方法，脚本和既有工具执行可确定的检查；它们各司其职，不互相复制整本手册。

项目入口可以把“发布／恢复”映射到 Delivery 和原 SOP／命令；已有文件不等于已经采用。稳定动作交给原脚本或 CI，AI 负责适用性判断、必要维护与结果核对。脚本跨版本复用，只有流程变化才更新；普通编辑不因此加载整套规范。

**能保证少用多少 Token、少出多少 Bug 吗？** 不能承诺固定比例。目标是减少重复实现、无关读取和返工；正确性、安全和可维护性优先。源码测试、宿主加载和模型效果是不同证据，验证边界见[评估说明](tests/behavior/host-evaluation.md)。

**Hook 会做什么？** 受支持的完整插件入口在生命周期事件中提供简短治理提示；纯 Skill 适配没有相同的自动注入能力。反馈进入本机待审箱，不自动上传或改写项目规则。首次启用及 Hook 变化需要审阅，详见[生命周期说明](docs/architecture/hook-lifecycle.md)与[安全说明](SECURITY.md)。

<a id="maintenance"></a>
<a id="安装更新与卸载"></a>
## 版本、更新与卸载

Senmu BuildOS 当前源码版本为 `v2.32.0`。源码、私有发布、公开市场版本和本机安装分别确认；上方徽章链接的是公开发布渠道，不能据此推断已安装版本。

<!-- product-surface-review: 2.32.0 -->

本版加强普通需求到产品、设计与工程的承接，统一持久 UI 规范入口和旧资料迁移方法，区分“未评估”与“没有 UI”。同时重写产品介绍，让八项能力的理念、做法与结果更容易理解；局部修改继续保持轻量。详见[用户更新日志](RELEASE_NOTES.md)。

<details>
<summary>更新已有安装</summary>

**Codex**

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

**Claude Code**

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

更新后新开会话；Claude Code 也可运行 `/reload-plugins`。确认实际来源、版本和启用状态，不把下载成功当成当前会话已更新。其他宿主使用上述适配文档中的更新方式，脚本方式需先取得拟安装的可信版本。

</details>

<details>
<summary>卸载</summary>

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

这些命令作用于对应安装范围；若安装时指定了范围，按客户端帮助定位相同范围。其他宿主按适配文档清理本插件的目录与安装记录，不删除同目录下其他人的 Skill、配置或项目数据。

</details>

<a id="contributing"></a>
<a id="参与项目"></a>
## 文档、反馈与贡献

使用问题请在[公开 Issues](https://github.com/SenMuShare/senmu-buildos/issues)说明宿主、BuildOS 来源与版本、复现步骤、预期和实际结果；请先脱敏。安全问题按 [SECURITY.md](SECURITY.md) 处理，不公开敏感信息。

欢迎报告真实使用问题，或通过 Fork（派生仓库）与 Pull Request（合并请求）贡献改进。你不必先读完全部规范才开始使用；贡献和发布检查见 [CONTRIBUTING.md](CONTRIBUTING.md)，后续方向见 [ROADMAP.md](ROADMAP.md)。三语文档维护规则见[贡献说明](CONTRIBUTING.md#github-readme-sync)。

## 许可证

[Apache License 2.0](LICENSE)。BuildOS 不能替代项目负责人、专业安全审计、云平台权限或 CI/CD；它也不是 OpenAI 或 Anthropic 的官方认证产品。
