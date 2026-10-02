# Senmu BuildOS — Agent Skills for Codex & Claude Code

**让 AI 先理解项目，再写对代码。**

*Understand the project. Reuse what works. Verify the result.*

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

森木 BuildOS 是一套面向真实项目的 AI 编程 Skills：帮助 Agent 看懂现有实现、厘清需求与约束，优先复用代码和成熟组件，再用匹配的测试与交付证据核对结果。从需求、UI/UX 和架构，到排障、代码评审和发布，按当前任务取用，不要求每次走完整流程。

**一个插件，八项按需能力。已有项目先沿用，小改动保持轻量。**

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

<a id="why"></a>
<a id="为什么需要-buildos"></a>
## 它解决什么问题

| 你遇到的问题 | BuildOS 的工作方式 | 你应该看到什么 |
| --- | --- | --- |
| 需求没弄清就开写，最后做偏了 | 先厘清范围、非目标和完成标准 | 实现与需求对应，而不是额外功能清单 |
| 不看旧代码，重复造组件和状态 | 先检查项目、框架与组件的现有能力 | 必要的小改动和明确的复用理由 |
| 越修越复杂，代码能跑却难维护 | 追踪根因、职责和调用方，验证真实行为 | 有证据的修复、清楚的边界和回归结果 |
| 换会话重新猜，测试通过就说已上线 | 把决定、进度和证据保存在项目已有位置 | 可继续的任务，以及实现、验收、发布的真实状态 |

BuildOS 适合希望持续维护真实项目的独立开发者、产品构建者和小团队。它不是代码生成器、托管执行平台，也不以更多文件和审批代替工程判断。

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
## 一个插件，八项能力

| 能力 | 什么时候使用 |
| --- | --- |
| [Project · 项目](skills/senmu-build-project/SKILL.md) | 接手项目，整理 AGENTS.md、现有规则与长期任务状态 |
| [Product · 产品](skills/senmu-build-product/SKILL.md) | 澄清需求、范围、优先级、界面内容和验收标准 |
| [Design · 设计](skills/senmu-build-design/SKILL.md) | 设计或评审 UI/UX、布局、交互、响应式与可访问性 |
| [Workflow · 工作流](skills/senmu-build-workflow/SKILL.md) | 定义业务 Agent、提示词、物料、恢复和交付约定 |
| [Engineering · 工程](skills/senmu-build-engineering/SKILL.md) | 理解系统、排障、架构设计、分语言规范、测试和代码评审 |
| [Delivery · 交付](skills/senmu-build-delivery/SKILL.md) | 复杂 Git 协作、版本、制品、获准的发布与回滚 |
| [Assurance · 核验](skills/senmu-build-assurance/SKILL.md) | 复现、实验、审计和证据充分性判断；独立评审需真实独立执行者 |
| [Learning · 学习](skills/senmu-build-learning/SKILL.md) | 复盘问题，将验证过的经验或外部方法写回适当规范 |

它们是平级能力，不是八个必须同时启动的代理。Python、TypeScript、Go、Java、Rust 等语言／运行时规范由 Engineering 按需读取，不把所有规范一起加载。入口名称即对应目录名，运行时说明采用英文；你可以用中文、英文、日文或其他语言协作。

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

这不是五份必建文件：小项目可以合并记录，成熟项目沿用已有 README、AGENTS.md、Issue、设计文档和质量命令。获得修改授权后，只补实际缺口，保留有效原则、项目例外和他人的工作。

**宜疏不宜堵。** 优先修正制造错误的需求、职责、接口或默认流程，测试与门禁控制重大剩余风险；原因清楚的小问题直接做最小修复。复用也不能以牺牲业务语义、安全、权限或兼容性为代价。

工作过程按需求理解、设计、实现、验证和交付衔接，任务越小，流程越轻。详细方法见[系统概览](docs/architecture/system-overview.md)、[Skill 边界](docs/architecture/skill-boundaries.md)和[项目产物映射](docs/architecture/project-artifact-map.md)。

<a id="faq"></a>
<a id="常见问题"></a>
## 常见问题

**每次都加载整套规范吗？** 不需要。已被项目规则和测试覆盖的普通修改，可以不调用专业 Skill；需要时才读取相关参考。实际加载取决于客户端与任务，不能仅凭文件存在判断生效。

**会自动改造项目、提交或发布吗？** 安装不授予这些权限。读取、修改、提交、推送和生产操作遵循用户授权与项目规则；只读请求保持只读，已批准的工作也不应被重复审批打断。

**只是另一份 AGENTS.md 吗？** 不是。AGENTS.md 保存项目常用原则与导航，Skill 提供当前任务需要的方法，脚本和既有工具执行可确定的检查；它们各司其职，不互相复制整本手册。

**能保证少用多少 Token、少出多少 Bug 吗？** 不能承诺固定比例。目标是减少重复实现、无关读取和返工；正确性、安全和可维护性优先。源码测试、宿主加载和模型效果是不同证据，验证边界见[评估说明](tests/behavior/host-evaluation.md)。

**Hook 会做什么？** 受支持的完整插件入口在生命周期事件中提供简短治理提示；纯 Skill 适配没有相同的自动注入能力。反馈进入本机待审箱，不自动上传或改写项目规则。首次启用及 Hook 变化需要审阅，详见[生命周期说明](docs/architecture/hook-lifecycle.md)与[安全说明](SECURITY.md)。

<a id="maintenance"></a>
<a id="安装更新与卸载"></a>
## 版本、更新与卸载

Senmu BuildOS 当前源码版本为 `v2.24.1`。源码、私有发布、公开市场版本和本机安装分别确认；上方徽章链接的是公开发布渠道，不能据此推断已安装版本。

<!-- product-surface-review: 2.24.1 -->

本版修复需求检查器的三项漏检，并补齐两条可运行的接口契约链路：模块化定义与代码声明生成，连接类型生成、真实调用校验和 SQLite 数据验证。增加故障注入与恢复测试，保留草稿、自定义版本、有效列表和 2.24.0 的轻量治理能力；原生 Agent 表现与源码验证分开报告。详见[用户更新日志](RELEASE_NOTES.md)。

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
