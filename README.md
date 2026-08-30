# Senmu BuildOS（森木 BuildOS）— Codex / Claude Code / 豆包项目治理插件

🌐 **文档语言：** **简体中文** | [English](./README.en.md) | [日本語](./README.ja.md)

> 让 Codex、Claude Code 和豆包（Doubao）在真实项目里少犯错、少返工、不断档，并用证据完成交付。

[![Validate Senmu BuildOS](https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg)](https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml)
[![License](https://img.shields.io/github/license/SenMuShare/senmu-buildos)](./LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social)](https://github.com/SenMuShare/senmu-buildos/stargazers)
[![Release](https://img.shields.io/github/v/release/SenMuShare/senmu-buildos)](https://github.com/SenMuShare/senmu-buildos/releases/latest)

Senmu BuildOS 是一个面向 **Codex、Claude Code 与豆包（Doubao）** 的开源 AI 编程项目治理插件。它把项目管理、产品需求、软件工程、Git 分支、测试验收、版本发布和经验反馈组织成七个按需加载的 Skill，帮助 AI 编程助手（Agent）先看懂真实项目再动手，而不是每次依靠一段越来越长的提示词临场发挥。

它不是传统的项目管理软件，也不会强迫成熟项目改成固定目录。当前支持 **OpenAI Codex**、**Claude Code** 和 **豆包（Doubao）**。

## 从常见失控到可持续交付

| 你经常遇到的问题 | BuildOS 带来的改变 |
| --- | --- |
| Agent 不看旧代码就新建目录、重复实现功能 | 开工前先识别项目根、现有实现和唯一事实负责人，优先复用和补齐 |
| 换会话、换 Agent 后又要从头解释 | 把进度、决定和证据留在项目自己的持久状态中，支持可靠接力 |
| 需求、代码、测试和文档互相打架，旧功能反复复活 | 追踪当前需求权威，并让替代、清理和回归验证作为一个变更闭环 |
| POC、Hotfix、长期分支和正式发布互相阻塞 | 按真实范围管理 Git 分支、worktree、候选版本和并行排除项 |
| “命令成功”被说成“已经完成或上线” | 分开验证实现、验收、制品、发布和生产事实，每个结论都有对应证据 |
| Skill 和提示词越来越长、Token 花在重复阅读上 | 七个专业 Skill 按任务加载，减少无关上下文、重复提醒和反复解释 |

## 把产品语言翻译成 Git 行为

人不应该为了和 AI 一起开发，先学会 branch、worktree、rebase 或 cherry-pick。你只需要说清楚产品意图，例如：

> 继续维护当前版本；另开一个长期版本；这几个反馈算同一批；先收进当前版本，但不要发布；确认没问题后发布。

BuildOS 负责把这些话翻译成工程动作：每次源码修改进入任务分支；并行写入使用独立 worktree；连续反馈在同一结果尚未封口时继续；长期版本使用继任线；任意 Agent 都能在自然收口时接收已完成修改，不需要固定 Team Leader。

项目只保留一个当前主线，并明确它是“始终可发布”还是“持续集成”。生产版本不从最新 `main` 猜测，而由冻结 commit、制品和真实发布记录确定。正式 Tag 只在目标发布事实验证成功后创建；部署前候选使用 commit、候选编号和制品身份冻结。“先不要发布”会保留为项目授权约束，不会因为换会话或提交代码自动消失。

## 30 秒开始使用

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
```

Claude Code 用户可使用：

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
```

豆包（Doubao）用户可先 clone 仓库后运行适配器安装脚本：

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos && python3 adapters/doubao/install_doubao.py
```

安装后刷新工具并开启新对话。完整的更新、卸载和 Hook 信任说明见[安装、更新与卸载](#安装更新与卸载)。

**快速导航：** [解决什么](#从常见失控到可持续交付) · [我们的特点](#我们的特点) · [安装与更新](#安装更新与卸载) · [怎样工作](#它怎样工作) · [七个 Skill](#一个插件七个平级-skill) · [当前边界](#当前边界)

## 我们的特点

1. **为 Agent 工作方式而设计。** BuildOS 的直接使用者是 AI Agent／Agent Harness；人负责目标、判断和授权，Agent 获得可执行、可恢复、可验证的项目工作契约。
2. **治理整个项目生命周期，而不只约束写代码。** 从项目初始化、需求与方案，到实现、工作流、测试、交付、生产事实和组织学习，关键事实始终有明确归属。
3. **尊重成熟项目，不强迫套目录。** 先只读识别已有入口、仓库、状态源和发布边界；默认目录只服务于新项目，已有项目在原 owner 上演进。
4. **一个插件，七个平级专业 Skill。** Project、Product、Workflow、Engineering、Delivery、Assurance、Learning 按任务路由，不设一个吞掉全部上下文的“总导演”。
5. **把记忆从聊天搬回项目。** 长任务使用持久状态、稳定标识、证据链接和恢复入口；聊天可以结束，项目不能失忆。
6. **让完成变成可以核验的事实。** 测试通过、制品生成、部署完成和生产可用是不同状态；BuildOS 要求在正确的层级留下相应证据。
7. **轻重随风险变化，并优先从源头解决问题。** 小任务保持轻量，高风险发布和数据操作保持 fail-closed；门禁只覆盖不能从源头消除的重要剩余风险。
8. **以工程教练而不是目录警察的方式工作。** Agent 先读真实现场和授权，判断当前属于什么场景，再给出首选建议、理由、可接受替代和收口条件；不用一套固定目录、分支或长清单代替专业判断。
9. **尊重用户意图，但不迎合未经核验的结论。** 用户决定目标、偏好和授权，Agent 区分期望、事实、推断与建议，依据项目证据和适用的外部权威知识独立判断；证据不足时明确不确定性。
10. **把上线后的资源和执行面一起收口。** 默认保留当前已验证版本和一个已验证回滚版本，项目明确策略优先；本机构建端、生产运行端、远程制品库及本次 Git 分支/worktree 分别核对，不用全局清理代替项目级闭环。
11. **做人和 Git 之间的翻译器。** 用户说版本、批次、是否集成和是否发布；BuildOS 自动选择分支、worktree、接收、候选与 Tag，并把安全复杂度留在系统内部。

## 它怎样工作

```text
识别真实项目 → 映射事实与 owner → 选择当前主 Skill → 执行并持久化状态
      → 用证据验收 → 交付／发布 → 复盘并反哺下一次改进
```

这不是要求每项工作机械走完固定流水线。BuildOS 会根据项目形态、任务目标和风险选择必要步骤：小型修改可以直接进入实现和验证；大型需求保留独立规格、方案、任务状态和验收；成熟项目先审视再演进；高风险交付才启用更强门禁。

## 开放迭代飞轮

Senmu BuildOS 既可以作为插件直接使用，也可以作为完整源码项目被 `clone` 或 `fork`。你可以在自己的分支中持续吸收网页、PDF、书、公开仓库或第三方 Skill 的有效经验，再选择保留为私有版本，或通过 Pull Request 回馈上游。

```text
安装正式版或 fork 源码
      → 在短分支中发现缺口、形成蒸馏批次
      → 读取 → 候选化 → 查重／冲突裁决 → 写回唯一 owner → 验证
      → 本地持续使用，或提交 Pull Request
      → 维护者审议、再蒸馏、合并并发布新版本
```

这里没有必须记忆的“暗号”。直接把目标和材料交给 Agent 即可，例如：

> 请读取这个网页、PDF、仓库或 Skill，把可复用的工程规则吸收到我的 BuildOS。合并同类项，拒绝不适用内容，不保存原始资料库，并用项目现有验证入口证明改进有效。

> 请在我的 fork 建立短分支，按 BuildOS 的知识蒸馏流程完成改进并准备 Pull Request；未经我授权不要推送或发布。

`clone` 用于把仓库下载到本机研究或修改；`fork` 是你在 GitHub 上长期维护的副本；`branch` 隔离每次改进；Pull Request 用于把成熟候选贡献回官方仓库。外部内容和社区贡献都先被视为不可信候选，只有通过来源与许可证检查、去重、冲突裁决、owner 映射、行为测试、上下文预算、整仓验证和 Skill 完整性复审后才会进入正式版本；发现问题必须整改并复核，当前审查对象与发布表面不一致时发布门禁会拒绝放行。详细执行方法见[贡献指南](CONTRIBUTING.md#开放迭代飞轮贡献流程)。

## 谁会需要它？

- 正在让 Codex 或 Claude Code 长期参与真实项目，而不只是生成一次性代码片段的个人或团队；
- 需要跨会话、跨 Agent 或跨工具持续推进复杂任务的项目；
- 已经拥有大量代码、目录、脚本和历史事实，不允许 Agent 再造一套体系的成熟项目；
- 同时包含软件、自动化、数据、内容、媒体、POC 或多种交付物的混合项目；
- 需要明确区分“做过、测过、交付过、发布过、生产可用”的严肃交付场景。

如果你也遇到过 Agent 重复建文件、忘记上下文、改乱项目或把“命令成功”说成“已经完成”，可以 **Star** 或 **Watch** 本仓库，跟踪 BuildOS 的后续发行与演进。

## 当前状态

Senmu BuildOS 当前正式版本为 `v2.0.1`，支持 **Codex 与 Claude Code** 共用七个平级 Skill，并分别提供插件清单、Marketplace 和生命周期 Hook 适配；**豆包（Doubao）** 使用同一组 Skill 和独立的引导适配（`adapters/doubao/`），以无 Hook 的用户 Skill 形式安装。所有适配层都不会改写用户全局配置或项目文件，也不联网；反馈收集只会把高信号候选写入本机 `~/.senmu-buildos/feedback/`，不在正常答复显示内部标记或 ID。安装、启用和卸载仍由用户显式控制。

## 安装、更新与卸载

### Codex 安装

需要已提供 `codex plugin` 命令的 Codex，以及可访问 GitHub 的 Git 环境。Senmu BuildOS 作为一个插件整体安装，七个 Skill 无需逐个下载。

```bash
codex plugin marketplace add SenMuShare/senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

安装完成后，重新启动或刷新 Codex，并开启一个新对话。首次启用或 Hook 内容变化时，请先在 Codex 中审查并信任 Hook；不要把“文件已经下载”误认为 Hook 已经运行。

### Claude Code 安装

需要支持 `claude plugin` 的新版 Claude Code：

```bash
claude plugin marketplace add SenMuShare/senmu-buildos
claude plugin install senmu-buildos@senmu-buildos
claude plugin list
```

插件 Skill 使用 `senmu-buildos:` 命名空间，避免覆盖用户已有 Skill。安装后可用 `/reload-plugins` 重新加载。Claude Code 适配注册 `SessionStart`、`SubagentStart` 和 `UserPromptSubmit`；不申请额外工具权限，不修改 `~/.claude` 或项目文件。`UserPromptSubmit` 只把明确纠正或投递动作写入本机待审反馈箱。

### Doubao（豆包）安装

豆包没有插件清单或生命周期 Hook，Skill 以文件夹形式放入 `workspace/.user_skills/`。有两种方式：

**方式 A：把仓库交给豆包，让豆包安装（推荐给不熟悉命令行的用户）。** 在豆包对话中粘贴仓库地址，让豆包读取 `adapters/doubao/README.md` 并按其说明把 `skills/` 下七个 `senmu-build-*` Skill 与 `senmu-build-kernel` 引导内核复制到豆包 `.user_skills`（剔除 Codex 专属的 `agents/` 元数据），详见[豆包适配器](adapters/doubao/README.md)。

**方式 B：clone 仓库后运行安装脚本。**

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos
python3 adapters/doubao/install_doubao.py --dry-run   # 预览，零写入
python3 adapters/doubao/install_doubao.py             # 安装到豆包 .user_skills
```

脚本会把七个 Skill 与 `senmu-build-kernel` 引导内核复制到 `.user_skills/`（剔除 Codex 专属的 `agents/` 元数据），并写入安装身份文件 `.senmu-buildos-install.json`。豆包无 Hook，治理内核不能像 Codex 那样每会话强制注入，`senmu-build-kernel` 以命中式引导提供；重复运行脚本即更新。

### Codex 更新

Codex 不会自动监视你的本机源码目录或 GitHub 提交。它更新的是 **Senmu BuildOS 插件**，不是分别追踪七个 Skill。仓库每次正式发行都会同时更新 `VERSION`、插件 manifest、Git Tag、Release 与 Marketplace 指向。更新时刷新 Marketplace，再重新安装插件：

```bash
codex plugin marketplace upgrade senmu-buildos
codex plugin add senmu-buildos@senmu-buildos
codex plugin list
```

随后重新启动或刷新 Codex，并开启新对话，让新的 Skill 清单和 Hook 生效。公开用户只应安装正式版本；如果你在本机直接修改源码，应先验证整仓影响，再为候选安装使用不同于正式版本的本地预发布版本或构建标识，避免 Codex 继续复用同版本缓存。

### Claude Code 更新

```bash
claude plugin marketplace update senmu-buildos
claude plugin update senmu-buildos@senmu-buildos
claude plugin list
```

维护者的统一版本准备、Tag 校验和 Release 制品流程见 [贡献指南](CONTRIBUTING.md#正式版本准备)。发布脚本只准备版本元数据，不会自行创建 Tag 或越过发布授权。

### 卸载

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

### 直接把仓库交给 Codex

也可以把下面这段话连同仓库地址交给 Codex。它要求 Agent 先审查再安装，不会把外部仓库当成天然可信：

> 请把 `https://github.com/SenMuShare/senmu-buildos` 作为 Codex 插件安装。先审查 `.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json`、`skills/` 和 `hooks/`，再按 README 添加 Marketplace、安装插件，并提醒我审查 Hook 信任。完成后只报告实际安装版本和启用状态。

交给 Claude Code 时，可以把“Codex 插件”改成“Claude Code 插件”，并要求它先审查 `.claude-plugin/`、`adapters/claude-code/`、`skills/`，以及 Hook 的有限本机反馈写入、无网络和不修改用户配置边界。

### 把仓库直接交给豆包

豆包用户可以直接把仓库地址或本 README 交给豆包，让豆包安装。豆包没有 Codex／Claude 的插件清单与 Hook，安装路径是读取 `adapters/doubao/README.md` 后把 Skill 复制进 `.user_skills`：

> 请把 `https://github.com/SenMuShare/senmu-buildos` 安装为豆包的用户 Skill。先读取 `adapters/doubao/README.md` 和 `adapters/doubao/install_doubao.py` 了解适配与安装逻辑，再把 `skills/` 下七个 `senmu-build-*` Skill 以及 `adapters/doubao/kernel/` 的 `senmu-build-kernel` 引导内核复制到豆包 `.user_skills`（剔除 `agents/` 与 `__pycache__`），并写入 `.senmu-buildos-install.json`。完成后只报告实际安装的 Skill 列表和版本。

## 核心设计哲学

- **新项目主动建立最小治理实例**：当用户明确要求创建或启动一个新项目时，Agent 应把项目分类、权威入口、最小目录和恢复方式作为正常启动工作的一部分，无需用户逐份列出要创建哪些文档。自动在这里指“任务触发后主动完成”，不指 SessionStart Hook 静默修改任意目录。
- **成熟项目先识别、再演进**：先只读确认项目真实入口、owner、状态源和交付边界，再经授权修复缺失、冲突、重复或过时结构；不为了套模板在老项目旁边再造一套目录和事实源。
- **全量源码治理有可核账的完成语义**：只有用户明确要求时才启用穷尽式模式，逐个登记第一方源码文件、函数／方法和现有注释；任一未审单元都会阻止完成结论，审查全覆盖与整改后符合标准分别验证。
- **日常代码质量在合并前收口**：不要求每个开发中的临时 commit 单独走审查，但每个进入集成基线的完整代码变更集都必须在合并前审查到变更文件、函数／方法和注释；批准绑定准确的 `base..head`，新增 commit 后自动失效，发布只核验这份审查证据与制品身份。
- **项目规范从真实证据中发现并按需读取**：成熟项目先从入口、实现、配置、测试和运行证据识别稳定规则，把完整内容写回原有专业 owner，只用短索引帮助 Agent 按当前任务选择相关规范，不创建第二套规范库，也不全文注入上下文。
- **项目 Agent 也有唯一契约**：只有确实维护自定义 Agent／系统提示词的项目才启用 Agent Definition System，以 Agent Register、稳定 Key／版本、单 Agent 唯一定义和确定性校验连接真实 Workflow／Harness；根 `AGENTS.md` 仍只是 Codex 项目入口，Skill 的 `agents/openai.yaml` 仍只是展示元数据。
- **实现遵循复用阶梯**：先判断是否需要实现，再依次查项目已有能力、标准库、平台原生能力、现有依赖和成熟开源方案；只有真实缺口仍存在时才写边界清楚的最少自有代码。
- **价值闭环先于基础设施绣花**：先形成可运行、可验证、可交付的最小价值闭环，再按真实反馈分阶段增强。不得让脚手架、抽象层、通用平台、检查清单或门禁建设长期先于核心路径完成。
- **宜疏不宜堵**：优先修正制造问题的需求、职责、架构、接口、数据 owner、默认值、实现和生产流程；门禁只处理无法从源头消除且足够重要的剩余风险。安全、隐私、权限、支付、生产数据、破坏性操作和正式发布完整性仍保留必要的 fail-closed 保护。
- **发布必须完成资源收口**：正式部署项目默认保留当前已验证版本和一个已验证回滚版本，项目明确策略优先。release 档位初始化项目级保留配置、精确制品／镜像清理脚本和契约测试；唯一发布入口在生产验证后分别收口运行端、构建端、按需远程制品库和本次 Git 执行面，不依赖 Agent 临场记忆或全局 prune。
- **上下文效率是一种架构能力**：通过单一事实源、短入口、清晰 owner、按需 Skill、任务切片和持久状态减少重复阅读、反复提醒、Token 消耗与多 Agent 接力歧义。
- **经过验证的经验进入飞轮**：Hook 自动捕获明确纠正、返工和回退；Agent 发现高信号缺口时可通过本机 CLI 静默提交，正常答复不显示内部标记或候选 ID。两条路径都只形成待审候选；由用户按需触发 Learning 集中查重、核证和处置。项目先在自己的事实和规则中完成修复，真正跨项目的候选经授权进入 BuildOS 源码项目并做整仓影响分析，而不是一次反馈就自动改写 Skill。

## BuildOS 与项目治理实例

Senmu BuildOS 是交给项目架构师和 AI Agent 的通用方法论、判断标准、默认实现与专业手册，不是任何具体项目的 PRD、技术方案或运行台账。每个项目都应形成自己的 **Project Governance Instance（项目治理实例）**，把适用原则落到项目自己的入口、目录、owner、状态源、质量命令和交付证据中。

```text
Senmu BuildOS：通用原则、专业方法、默认结构、判断标准
                         ↓ 校准
Project Governance Instance：具体项目选择、映射和演进后的治理实例
                         ↓ 运行
项目本地需求、代码、任务／运行状态、验证、交付与发布事实
                         ↓ 验证后反哺
Senmu BuildOS 的下一次通用演进
```

项目实例统一的是职责和语义，不是物理外形。大型软件可以使用 PRD、架构契约和发布体系；小型脚本可以把职责合并到 README、测试和版本记录；成熟工作流可以继续以任务包、数据库、manifest、Makefile 和回执作为 owner。Python、TypeScript、Go、Java、前端框架和通用代码质量等稳定知识保留在 BuildOS 中按需查询，项目只保存自己的选型、约束、入口、例外与验证命令。

### 两类权威

- **事实权威**：项目本地代码、文档、数据库、运行状态和发布回执说明项目当前是什么，默认模板不得覆盖真实事实。
- **治理标准**：BuildOS 用于判断当前事实链是否完整、清晰、可恢复、可验证和可演进。已有规则不因存在就自动正确；缺失、冲突、重复、过时或不可搬迁时，应在授权后治理原 owner。

因此，尊重老项目不等于冻结老项目。正确做法是先识别现状，再提出目标实例和迁移边界，最后升级、合并或补齐原 owner，而不是建立长期并行体系。

## 源码项目与安装运行形态

Senmu BuildOS 在 GitHub／Git 中是一个完整且独立的产品项目：插件清单、全部 Skills、Hooks、文档、脚本和测试共同组成同一个源码仓库和发布单元。Codex 与 Claude Code 都安装整个插件，并把其中七个 Skill 暴露为按需入口；这些 Skill 不是七个彼此独立版本化的产品。

因此，一次 BuildOS 改进必须先站在整个仓库视角检查影响。最终可能只修改某个 Skill、一份 Markdown 或一个脚本，但仍要确认相邻 owner、路由、模板、Hook、测试和发布信息是否一致。应用项目经验、BuildOS 源码修改、候选安装和公开发布分别拥有独立状态与授权，不能相互冒充完成。

### 五种项目能力

| 能力 | 适用对象 | 行为 |
| --- | --- | --- |
| Recommend Placement | 单个文档、目录或职责 | 结合现有 owner 给出首选位置、理由和替代，不因咨询自动创建 |
| Plan / Initialize New Project | 空白或明确的新项目 | 先用显式分类、档位和模块零写入规划；授权后按已审阅方案生成实例 |
| Assess Existing Project | 已有项目 | 先零写入盘点权威入口、发布单元、候选与排除证据，再语义确认 owner、缺口、冲突和迁移风险 |
| Evolve Existing Project | 已完成审视并取得授权的项目 | 在原 owner 上补缺失、修冲突、合并重复、迁移不可搬迁路径并验证恢复能力 |
| Govern a Mature Project | 需要跨阶段接管的历史混乱项目 | 用唯一持久任务串联只读基线、Finding 裁决、用户授权、分波整改、复核、恢复和临时内容去留 |

`senmu-build-project` 提供零写入 `--mode plan-new`、显式实施 `--mode initialize-new`、只读 `assess_project_governance.py` 和可选的成熟项目接管控制记录校验器。项目类型和档位必须显式提供，`--modules` 可覆盖类型推荐。评估脚本默认只输出有界摘要，`--verbose` 才展开完整候选清单；脚本结果标记为候选盘点，不能代替语义审视。成熟项目仍先给方案，再根据证据和用户授权执行。

`core` 是真正的轻量档位：只建立 README、AGENTS、治理章程、机器 policy 和一个验证入口，不预建任务、日志、经验或各专业文档。需要持续协作、持久任务和专业 owner 时使用 `standard`；需要正式部署、发布和制品收口时使用 `release`。`plan-new`（以及兼容的 `--dry-run`）只输出 JSON，并以 `planned` 列出候选文件，保持零写入。

`Initialize New Project` 是由“创建／启动新项目”这一任务语义触发的 Agent 行为：Agent 应主动选择 `senmu-build-project`、根据目标和证据完成分类，并在实质实现前生成最小实例。它不是一个监听所有新目录的后台进程，也不会由 Hook 对非空目录自动写入。

项目确实维护自定义 Agent／系统提示词时，可在空白新项目初始化时显式增加 `--with-agents`。它只增加 `agents/AGENT_REGISTER.md`、Agent Definition 模板与校验器，不会替每个项目虚构 Agent，也不会把根 `AGENTS.md` 或 Skill 元数据转成业务 Prompt。

## 一个插件，七个平级 Skill

| Skill | Professional Name | 中文职责 | 何时加载 |
| --- | --- | --- | --- |
| `senmu-build-project` | Project Management | 项目管理 | 项目初始化、目录或权威冲突、治理档位、持久任务状态、跨生命周期协调 |
| `senmu-build-product` | Product Management | 产品与需求管理 | 需求收集、PRD、优先级、路线图、迭代承诺、验收与范围变化 |
| `senmu-build-workflow` | Workflow Governance | 工作流与物料治理 | Harness、Agent 契约、数据／素材流、运行状态、恢复、交付物和回执 |
| `senmu-build-engineering` | Software Engineering | 软件工程治理 | 技术选型、架构、实现经济性、编码、测试、重构、依赖和技术债 |
| `senmu-build-delivery` | Delivery Management | 协作、版本与交付管理 | Git、仓库和发布单元、版本、制品、部署、发布、生产验证和回滚 |
| `senmu-build-assurance` | Governance Assurance | 治理审查与证据保证 | POC、只读审查、债务盘点、证据分级和争议性因果核验 |
| `senmu-build-learning` | Organizational Learning & Continual Improvement | 组织学习与持续改进 | 复盘、经验沉淀、知识维护、源头改进和 BuildOS 整仓反哺 |

七个 Skill 在技术上和职责上平级。`senmu-build-project` 不是必须先加载的父 Skill；已有稳定项目中，单领域任务应直接加载对应 Skill。只有任务确实跨越职责边界时才组合第二个 Skill，也不应一次加载整套内容。

Codex 根据各 Skill 的 `description` 和用户期望结果选择当前主 Skill；用户也可以显式指定。职责真正发生切换时，当前 Skill 只交接标识、范围、权威入口、事实与证据、未决问题、下一项结果和授权边界，不复制整套规范。Senmu BuildOS 不设置第八个“总导演”Skill，也不把七个 Skill 组成固定流水线。

## 三层工作方式

```text
Codex／AI Agent
├── 生命周期 Hook：恢复极短、跨领域且不可遗漏的治理底线
├── 专业 Skill：按当前目标加载一个主领域，必要时组合一个支持领域
└── 项目本地事实：README、AGENTS、policy、schema、代码、任务、台账和发布证据
```

项目本地事实是当前状态的权威，Senmu BuildOS 是审视和演进这些事实的治理标准。BuildOS 帮助建立、定位、验证和改善 owner，但不在插件内部保存某个具体项目的需求、进度或发布状态。

### 生命周期 Hook

`SessionStart` 在启动、恢复、清空或上下文压缩后注入不超过 950 字符的固定治理内核；`SubagentStart` 注入不超过 500 字符的委派边界。`UserPromptSubmit` 只匹配明确纠正或投递动作，仅询问反馈机制不入箱；Agent 发现高信号治理缺口时可用本地 CLI 静默提交。命中项经脱敏、去重后写入本机反馈箱，正常答复不显示内部标记或候选 ID。Hook 不读取整个项目、不猜当前岗位、不加载 Skill 全文，也不自动修改任务状态或晋级规则。

这样可以恢复“真实项目优先、不得越权、按需加载、保留证据、未验证不算完成”等底线，同时避免把产品、工程和发布规则反复塞入每一轮上下文。插件 Hook 安装或变化后仍需由用户在 Codex 中审查并信任，源码存在不等于运行时已经启用。

### 持久任务状态

需要多个依赖步骤、阶段、Agent 或会话的工作，必须拥有项目声明的 **Durable Task State Owner**。`governance/tasks/` 是 BuildOS 为 standard/release 新项目提供的默认实现；core 可沿用 README、Issue 或外部任务系统，成熟项目则映射并沿用已有任务包、数据库或外部系统。

默认 Markdown 实现为：

- `TASK_REGISTER.md` 只登记任务及其当前状态。
- `TASK-<NNNN>-<slug>.md` 是一个带编号的持久任务计划，保存边界、阶段、进度、关键决定摘要、证据链接和恢复入口；默认不为每个任务建立独立目录。
- PRD、技术设计、Run Manifest、测试证据、Release Record 等专业事实仍写入各自唯一 owner，任务记录只链接，不复制正文。

Codex 的临时计划适合当前会话调度；项目任务需要分步骤、分阶段、跨 Agent、跨会话、审计或恢复时，才建立编号任务计划。二者不做机械双写。

## 目录

```text
.agents/         Git Marketplace 安装使用的公开插件目录
.github/         复用本地验证入口的仓库级 CI
.codex-plugin/   Codex 插件身份和展示元数据
.claude-plugin/  Claude Code 插件身份和 Marketplace
adapters/        Codex、Claude Code 与豆包（Doubao）的 Harness 适配
hooks/           Codex Hook 入口与共用短治理内核
bin/             本机反馈候选查询、提交与审议入口
skills/          七个按需加载的专业 Skill
docs/            系统架构、职责边界和项目产物地图
scripts/         插件包结构、产品身份和链接校验
tests/           Hook、项目初始化、包结构和行为场景测试
```

这是可公开源码面，由项目的私有权威库按白名单生成；内部任务、工作日志、原始反馈、本机路径和私有审查不进入该仓库。详见 [源码公开边界](docs/architecture/publication-boundary.md)。

具体职责见 [Skill 边界与协作关系](docs/architecture/skill-boundaries.md)，项目内文件落点见 [项目产物与目录责任地图](docs/architecture/project-artifact-map.md)，Codex 与 BuildOS 的分工见 [Codex Harness 责任边界](docs/architecture/codex-harness-boundary.md)。

## 与 Harness 官方机制的对齐

- 使用一个插件交付多个相关 Skill，而不是要求用户逐个安装七个孤立 Skill。
- 每个 Skill 以简短 `description` 完成发现和触发，完整入口只负责路由，详细知识按需进入 `references/`。
- Codex 使用 `hooks/hooks.json` 和 `${PLUGIN_ROOT}`；Claude Code 使用 `.claude-plugin/plugin.json`、`${CLAUDE_PLUGIN_ROOT}` 和独立 Hook 配置。
- Claude Code Skill 自动进入插件命名空间，不覆盖用户现有 Skill；两个平台共享短治理上下文和有限本机反馈候选协议。
- 项目自己的入口文件、权限、沙箱、会话计划和上下文压缩仍由 Harness 负责，BuildOS 不复制宿主已经可靠拥有的状态。

## 验证

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

GitHub Actions 只复用以上三个项目自有入口。Skill 还应分别通过 Skill Creator 的 `quick_validate.py`，插件清单应通过 Plugin Creator 的 `validate_plugin.py`。格式和静态断言通过不代表真实 Agent 路由、Hook 信任或任务行为已经验证；这些仍需在隔离的候选环境中完成行为测试。

## 当前边界

- `v1.0.0` 是首个面向 Codex 的正式源码发行版，Tag、GitHub Release、`VERSION`、插件版本和 Changelog 指向同一基线。
- Git Marketplace 的安装、更新和卸载入口已经完成命令级验证；Hook 是否可信、是否启用，以及真实任务中的 Skill 路由仍须在当前 Codex 环境中分别验证。
- `v1.1.0` 正式支持 Codex 与 Claude Code；Claude Code 适配已经通过官方清单校验、隔离安装／卸载冒烟、Hook 协议和副作用边界验证。
- 当前已覆盖低噪声反馈候选收集、集中审议、复盘和组织学习，但不提供反馈看板、统计或自动规则生成；增长和指标等完整业务运营方法论仍不在当前范围内。
- 本仓库采用 [Apache License 2.0](LICENSE)；许可证允许使用、修改和分发源码，但不会扩大当前明示的平台与兼容性承诺。

## 许可证

Senmu BuildOS 以 [Apache License 2.0](LICENSE) 开源。
