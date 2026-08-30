# Senmu BuildOS（森木 BuildOS）— AI 编程项目的工程教练与运行规范

<p align="center">
  让 Codex、Claude Code 和豆包先把事情做对，再用更少的无效代码把它做好。
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a> · <a href="README.ja.md">日本語</a>
</p>

<p align="center">
  <a href="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml"><img src="https://github.com/SenMuShare/senmu-buildos/actions/workflows/validate.yml/badge.svg" alt="Validate Senmu BuildOS"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SenMuShare/senmu-buildos" alt="License"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/stargazers"><img src="https://img.shields.io/github/stars/SenMuShare/senmu-buildos?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/SenMuShare/senmu-buildos/releases/latest"><img src="https://img.shields.io/github/v/release/SenMuShare/senmu-buildos" alt="Release"></a>
</p>

Senmu BuildOS 是一个面向 **AI coding agent** 的开源项目运行规范和软件工程教练。它覆盖需求、技术设计、框架与组件选型、前后端实现、测试、Git、版本发布和经验反馈，帮助 Agent 在真实项目里持续交付，而不是每次依靠一段越来越长的 Prompt 临场发挥。

它重点解决两件事：

1. **让项目执行更规范，少犯错。** 先确认真实需求、项目事实和授权，再让设计、代码、测试、分支、版本与发布证据彼此对应。
2. **提高代码质量，减少无效代码和上下文浪费。** 先判断需求是否真的需要实现，再依次复用项目已有能力、框架／组件公开 API、平台、标准库和成熟依赖；只有真实缺口才写边界清楚的最小自有代码。

> BuildOS 追求的是“更少但正确的代码”，不是机械追求最少行数或最低 Token。安全、可访问性、业务语义、测试和可维护性不会为了省 Token 被删掉。

## 为什么需要 BuildOS

| AI 编程常见问题 | BuildOS 的工作方式 |
| --- | --- |
| 需求还没说清就开写，顺手增加一堆没有要求的功能 | 用范围、非目标和可验证验收约束实现；未批准想法留在需求候选，不进入本次代码 |
| 不看旧代码就新建目录、服务和第二套状态 | 先识别项目入口、现有代码、调用链和唯一数据来源，优先扩展已有能力 |
| 框架一个参数能解决，Agent 却手搓组件、监听 DOM、复制状态 | 先检查当前版本的公开 API 和组件能力；只有证据证明不满足时才做最小适配 |
| 代码能跑，但职责混乱、难读、难测、越改越像“屎山” | 用唯一事实、模块边界、显式副作用、变化局部性、回归测试和可删除性约束实现 |
| 为未来假设预建抽象、插件系统和通用平台 | 先闭合当前最小价值切片；第二个真实用例或明确路线图再触发扩展 |
| 换会话或换 Agent 后重新解释，重复读取大段规则 | 把决定、进度和证据写回项目文档与任务；只在需要时读取相关规则，并复用仍然有效的信息 |
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

## 它怎样工作

BuildOS 不只在“写代码”这一步检查格式，而是在更早的位置阻止错误进入代码：

```text
真实问题与已批准范围
        ↓
项目事实、架构边界与现有能力
        ↓
技术路线、框架、组件与公共扩展点
        ↓
最小正确的前端／后端实现
        ↓
匹配风险的测试与产品验收
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
- **先复用，再自研。** 优先使用项目、框架、组件、平台和标准库的公开能力；确有缺口时再做最小适配。
- **任务越小，流程越轻。** 普通修改只做必要检查；数据、权限、支付、生产发布等高风险工作保留设计、验证和回滚依据。
- **用证据说明完成。** 测试通过、产品验收、制品生成、部署成功和生产可用是不同的事实，不能互相替代。
- **让项目自己记住。** 重要决定、进度和恢复入口写回项目，而不是依赖某一次聊天一直存在。

更完整的系统设计见[系统概览](docs/architecture/system-overview.md)、[Skill 边界](docs/architecture/skill-boundaries.md)和[项目产物映射](docs/architecture/project-artifact-map.md)。

## 适合哪些场景

- **新项目**：从目标出发建立最小需求、架构、质量与交付基线，不一次生成一座文档城堡。
- **成熟老项目**：先只读识别已有 README、配置、代码、测试、CI 和发布事实，再补缺口，不重建第二套治理目录。
- **普通功能或 Bug**：以项目本地规则为主，复用框架和现有实现，做最小改动与匹配验证。
- **复杂长任务**：把阶段、决定、证据和恢复入口留在项目中，支持跨会话和多 Agent 接力。
- **正式发布**：让范围、审查、测试、版本、制品、部署、生产核验和回滚身份一致。
- **项目治理与学习**：审查技术债和重复实现，把经过验证、能够跨项目复用的经验沉淀为规则。

## 一个插件，七项能力

| 能力 | 什么时候使用 |
| --- | --- |
| `senmu-build-project` | 新项目建立基本秩序，或老项目需要识别现有结构、规则和长期任务状态时 |
| `senmu-build-product` | 需要明确需求、范围、优先级、路线图或验收条件时 |
| `senmu-build-workflow` | 需要设计多步骤流程、Agent 分工、物料流转、恢复和交付状态时 |
| `senmu-build-engineering` | 需要做技术设计、架构选型、代码质量、测试、重构或技术债治理时 |
| `senmu-build-delivery` | 需要处理复杂 Git 协作、版本、制品、发布、回滚或生产核验时 |
| `senmu-build-assurance` | 需要独立复现、POC、审查或证据充分性判断时 |
| `senmu-build-learning` | 需要复盘问题、审议反馈或把外部知识沉淀成通用规则时 |

普通代码修改如果已经被项目 `AGENTS.md`、框架和测试清楚约束，可以不加载 BuildOS 专业 Skill。需要时也只选择当前最匹配的 Skill 和 reference，而不是把七份手册一次塞进上下文。

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

Senmu BuildOS 当前正式版本为 `v2.0.6`，支持 Codex、Claude Code 和豆包适配。安装的是整个插件，不需要逐个下载七个 Skill。

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

### 卸载

```bash
codex plugin remove senmu-buildos@senmu-buildos
codex plugin marketplace remove senmu-buildos

claude plugin uninstall senmu-buildos@senmu-buildos
claude plugin marketplace remove senmu-buildos
```

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
