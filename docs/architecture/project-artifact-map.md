# 项目产物与目录责任地图

本地图规定八个 Senmu BuildOS Skill 为新项目提供的默认 owner，以及已有项目映射和演进 owner 的规则。目录服务于事实类型，不按 Agent 名称建立。已有项目先把真实入口作为事实权威；若 owner 完整且合理则登记并沿用，若存在缺失、冲突、重复、过时或不可搬迁问题，则在授权后治理原 owner，不建立平行副本。

初始化模板的物理 owner 与项目内产物 owner 保持一致：Project 负责项目入口、地图、任务和治理模板；Product、Design、Workflow、Engineering、Delivery、Assurance、Learning 分别持有本域的规则或初始化模板。Project 的初始化器只做组合和渲染，不拥有其他领域的第二份模板。

## 三种物理布局

- **Software Repository**：项目根就是 Git 仓库；`product/`、`engineering/`、`governance/`、`delivery/`、`operations/` 与代码位于同一仓库。
- **Project System**：面向媒体、内容、工作流、运营和 POC；只有 `00-project-system/` 是 Git 仓库，专业规则、流程、代码、配置和索引位于其中，大型源输入、工作区、交付物和归档位于其外。
- **Publication Workspace**：私有权威库、可重建的公开 Git 投影和临时发布 staging 是同一工作区下的并列路径角色。具体名称由项目实例选择，Skill 只保存工作区内相对路径。

初始化器不因使用 `release` 档位就创建制品目录。只有需求、技术架构和真实安装／部署／交付消费者共同证明某种制品存在时，才增加对应构建、验证、保留与回滚 owner。

`workflows/`、`engineering/` 等是同一项目系统内的专业模块，不自动成为独立 Git 仓库或发布单元。是否拆仓由真实构建、部署、团队、权限和发布边界决定。

## 统一命名

| 概念 | Professional Name | 默认路径／命名 |
| --- | --- | --- |
| 项目治理章程 | Project Governance Charter | `governance/GOVERNANCE.md` |
| 项目地图 | Project Map | `governance/PROJECT_MAP.md` |
| 项目规范索引 | Project Standards Index | standard/release 新项目位于 `governance/PROJECT_MAP.md` 的短索引区；成熟项目映射已有入口 |
| 治理策略 | Governance Policy | `.senmu-buildos/config.json` |
| 任务登记表 | Task Register | standard/release 新项目默认 `governance/tasks/TASK_REGISTER.md`；core 与成熟项目可映射或合并到原生 owner |
| 任务计划与状态记录 | Task Plan & Status Record | standard/release 新项目默认 `governance/tasks/TASK-<NNNN>-<slug>.md`；core 与成熟项目可映射计划文件、Issue、数据库或外部对象 |
| 协作工作日志 | Work Log | `governance/logs/WORKLOG.md` |
| 经验与防回退台账 | Lessons Learned Register | standard/release 默认 `governance/lessons/LESSONS_LEARNED.md`；core 按需晋级 |
| 经验台账校验器 | Lessons Learned Validator | BuildOS 新项目默认 `.senmu-buildos/validate_lessons.py`；由治理 policy 声明调用方式 |
| Agent 登记表 | Agent Register | 启用项目 Agent 治理时使用 `agents/AGENT_REGISTER.md` |
| Agent 定义 | Agent Definition | `agents/<agent-key>/AGENT.md`；一个 Agent 一个唯一现行契约 |
| Agent 定义模板 | Agent Definition Template | `.senmu-buildos/templates/agent/AGENT.md`；模板不是生效定义 |
| Agent 定义校验器 | Agent Definition Validator | `.senmu-buildos/validate_agents.py`；校验登记、Key、版本、状态、路径与核心章节 |
| 用户需求 | User Requirements | `product/USER_REQUIREMENTS.md`；可选需求池，状态和处理版本写在条目旁 |
| 版本产品需求文档 | Product Requirements Document | `versions/<version>/PRD.md` |
| 产品规格书 | Product Specification | `product/PRODUCT_SPECIFICATION.md`；当前完整产品事实 |
| 界面设计系统／规范 | Interface Design System / Specification | 项目已有设计系统、组件主题或 `design/`；只在存在跨页面稳定设计事实时建立 |
| 工作流契约 | Workflow Contract | `workflows/<workflow-id>/WORKFLOW.md` 或项目既有定义入口 |
| 运行清单 | Run Manifest | `state/runs/<run-id>.json`、运行数据库或编排系统 |
| 运行回执 | Run Receipt | `evidence/runs/<run-id>/` 或项目既有证据系统 |
| 版本技术设计 | Technical Design | `versions/<version>/TECHNICAL_DESIGN.md`；按需 |
| 版本测试用例 | Test Cases | `versions/<version>/TEST_CASES.md`；依据 PRD，深度按风险 |
| 架构决策 | Architecture Decision Record | `engineering/decisions/ADR-<NNNN>-<slug>.md` |
| 系统技术规格书 | System Technical Specification | `engineering/SYSTEM_TECHNICAL_SPECIFICATION.md`；当前完整技术事实 |
| 技术债登记 | Technical Debt Register | `engineering/TECH_DEBT.md` |
| 测试策略 | Testing Strategy | `engineering/TESTING_STRATEGY.md` |
| 版本与发布计划 | Version and Release Plan | `delivery/RELEASE_PLAN.md` |
| 仓库与发布单元登记表 | Repository and Release Unit Register | `governance/REPOSITORY_AND_RELEASE_UNITS.md` |
| 制品清单 | Artifact Manifest | 制品库元数据或 `evidence/releases/<release-id>/ARTIFACT_MANIFEST.json` |
| 发布记录 | Release Record | 发布系统或 `evidence/releases/<release-id>/RELEASE_RECORD.md` |
| 部署手册 | Deployment Guide | `operations/DEPLOYMENT.md` |
| 发布保留配置 | Release Retention Configuration | `operations/release-retention.env` |
| 发布制品收口脚本 | Release Artifact Cleanup | `operations/scripts/cleanup-release-assets.sh` |
| 实验登记表 | Experiment Register | `experiments/EXPERIMENT_REGISTER.md` |
| 实验包 | Experiment Package | `experiments/EXP-<NNNN>-<slug>/` |
| 实验清单 | Experiment Manifest | 实验包内 `experiment-manifest.json` |
| 审查报告 | Assurance Review Report | `engineering/audits/`、`evidence/reviews/` 或项目审计系统 |

文件名使用稳定英文大写词组和下划线；编号对象使用固定前缀与四位序号，例如 `TASK-0001-<slug>.md`、`REQ-0001-<slug>.md`、`TD-0001-<slug>.md`、`ADR-0001-<slug>.md`、`EXP-0001-<slug>/`。目录使用小写英文 kebab-case。不要同时建立 `task/`、`tasks/`、`work-items/`、`plans/` 等多个近义任务目录。

## 八个 Skill 的默认项目落点

| Skill | 项目内权威产物 | 默认位置 | 不应写入 |
| --- | --- | --- | --- |
| `senmu-build-project` | 项目治理章程、项目地图、任务登记与编号计划、治理 policy 和工作日志 | 新项目默认 `governance/`；成熟项目映射并演进已有 owner | 产品正文、技术实现、运行状态、经验规则或发布结果的复制件 |
| `senmu-build-product` | 可选用户需求、每版本 PRD、当前产品规格、跨页面界面内容标准和产品验收事实 | `product/`、项目既有设计系统与 `versions/<version>/PRD.md`；不为文案另建平行台账 | 技术实现决定、部署事实、任务执行状态副本 |
| `senmu-build-design` | 视觉方向、设计 Token、组件表现、布局、响应式、交互、动效、可访问性和界面评审决定 | 项目已有设计系统、组件主题、原型入口或按需 `design/`；一次性调整留在现有实现 owner | 产品功能／文案、组件库 API、技术架构、独立审查结论或平行设计系统 |
| `senmu-build-workflow` | 流程契约、项目 Agent 定义、schema/config、输入、工作区、运行状态、交付物、证据和归档 | 项目系统内 `workflows/`；启用时使用 `agents/`；物料型项目外部角色目录由 Project Map 映射 | 软件架构正文、版本发布计划、第二份任务登记表或根 `AGENTS.md` 的复制件 |
| `senmu-build-engineering` | 当前系统技术规格、按需版本技术设计、测试用例、选型、代码质量、技术债、ADR、语言／框架规则和测试策略 | `engineering/`、`versions/<version>/`；测试代码与 fixtures 位于项目既有 `tests/` 或语言生态目录 | 产品优先级、发布批准、独立审查结论 |
| `senmu-build-delivery` | 分支与合并、发布单元、版本、changelog、制品、部署、回滚、线上验证 | `delivery/`、`operations/`、各发布单元及适用的发布证据 owner | 需求正文、工程设计副本、未发生的发布状态 |
| `senmu-build-assurance` | POC 账本、实验 manifest、独立审查报告和可复查证据 | `experiments/`、`engineering/audits/`、适用的 `evidence/reviews/` | 未获授权的修复、第二份工程规范、经验台账或任务状态 |
| `senmu-build-learning` | 复盘、经验与防回退条目、经验索引、状态和替代关系 | standard/release 默认 `governance/lessons/LESSONS_LEARNED.md`；core 按需晋级，成熟项目映射既有知识 owner | 工作日志副本、专业规则正文、未验证猜测或应用项目之外的自动修改 |

新工作流／媒体／数据项目默认只让 `00-project-system/` 进入 Git，并在其外使用 `01-sources/`、`02-workspace/`、`03-deliveries/`、`04-archive/`。已有项目使用 `00_项目系统`、`inputs`、`staging`、`data`、`outputs` 或 `receipts` 时，不为统一字面名称而迁移；应在 Project Map 登记标准角色、实际路径和 Git 边界。

其中 `senmu-build-project` 拥有 Work Log 的目录、schema 和生命周期，`senmu-build-learning` 拥有 Lessons Learned Register 的语义、schema 和生命周期。其他 Skill 可以向统一 Work Log 追加本域已经发生的工作，或向 Learning 提交候选经验；根因需要独立裁决时由 `senmu-build-assurance` 提供证据。只有满足晋级条件的经验才写入项目统一台账，不得再建立专业 Skill 私有的第二份工作日志或经验台账。

## 入口、配置与状态的单一职责

| 文件 | 只负责 | 不负责 |
| --- | --- | --- |
| `AGENTS.md` | Codex 自动加载的项目差异层：身份、作用域、权威路由、真实命令、特有约束和明确覆盖 | BuildOS 通用规则副本、项目百科、当前任务正文或专业手册复制件 |
| `agents/AGENT_REGISTER.md` | 项目业务 Agent 的 Key、版本、状态、定义和运行入口索引 | Prompt 正文、运行状态或 Skill 展示元数据 |
| `agents/<agent-key>/AGENT.md` | 单个项目业务 Agent 的稳定角色、Prompt 与执行契约 | 单次任务参数、当前 step／attempt／checkpoint 或根目录读取入口 |
| `.senmu-buildos/templates/agent/AGENT.md` | 创建新 Agent Definition 的结构模板 | 已生效 Agent、当前版本事实或运行配置 |
| `.senmu-buildos/validate_agents.py` | Agent 登记、命名、版本、状态、路径和核心章节的确定性结构检查 | 自然语言质量裁决、运行验证或业务验收 |
| `README.md` | 人和 AI 都可读的项目定位、启动方式与关键入口 | 当前任务状态副本 |
| `governance/GOVERNANCE.md` | 项目核心原则、权威顺序、治理版本、修订与例外 | 需求、设计、任务、运行或发布事实正文 |
| `.senmu-buildos/config.json` | validator 使用的静态结构化治理配置，包括主线语义、直接主线写入禁止、worktree 根、Change Unit 状态、正式 Tag 语义和授权模式 | 当前目标、进度、待接收列表、下一步或聊天状态 |
| `governance/PROJECT_MAP.md` | 模块、目录、状态源、公开入口、交付单元、legacy 和任务相关规范入口的导航 | 活跃任务、专业正文或规范全文副本 |
| standard/release 默认 `governance/tasks/TASK_REGISTER.md` 或项目映射 owner | 当前与历史受管理任务索引 | 单个任务正文 |
| standard/release 默认 `governance/tasks/TASK-<NNNN>-<slug>.md` 或项目映射对象 | 单个任务计划、当前边界、进度、关键决定摘要、证据和恢复入口 | 专业事实正文、完整聊天或时间流水 |
| `governance/logs/WORKLOG.md` | 已发生工作的追加时间线 | 当前状态、计划或长期规则 |
| standard/release 默认 `governance/lessons/LESSONS_LEARNED.md` 或项目映射 owner | 经验证且可复用的长期项目经验 | 单次问题、原始审查报告或工作流水 |
| `.senmu-buildos/validate_lessons.py` | 经验条目结构、状态、证据字段、替代关系、疑似重复与明显敏感信息检查 | 根因裁决、自动合并、自动晋级或专业规则正文 |
| Workflow Contract | 长期流程、输入输出、步骤、状态转换和恢复规则 | 某次运行的当前 step、attempt 或结果 |
| Run Manifest／运行数据库 | 某次运行的输入快照、步骤状态、checkpoint、错误和输出引用 | 项目目标、跨阶段计划、产品验收或发布结论 |
| Run Receipt | 对一次运行结果和外部副作用的验证证据 | 运行状态 owner 或交付状态 owner |
| Version and Release Plan | 发布范围、候选规则、门禁、授权和回滚计划 | 已发生的部署动作或生产状态 |
| Artifact Manifest | 候选制品的来源、哈希、平台和质量证据 | 用户授权或生产发布结论 |
| Release Record | 一次发布／回滚尝试的授权、动作、验证和结果 | 产品验收正文、工程测试正文或动态运行平台状态 |
| Release Retention Configuration／Cleanup | 受管制品根、镜像仓库、当前／上一版本、Pin 与项目级精确清理 | Git 历史、数据库、Volume、其他项目对象或全局 Docker 清理 |
| Experiment Package／Manifest | 实验问题、变量、运行、有效性、评价与结论证据 | 正式 ADR、生产批准或项目任务进度 |
| Assurance Review Report | 冻结对象、覆盖、证据、发现、盲区和审查结论 | 被审领域的规范正文、未获授权的修复或长期任务状态 |

## 同一任务如何跨 Skill

```text
Durable Task State Owner             当前边界、阶段、进度、证据链接、恢复入口
├── versions/<version>/PRD.md        本版本产品范围、行为与验收事实
├── product/PRODUCT_SPECIFICATION.md 当前完整产品事实
├── design/...                       跨页面视觉、交互与设计系统事实（如项目需要）
├── workflows/...                    流程、运行和物料事实
├── agents/<agent-key>/AGENT.md       项目 Agent／Prompt 的稳定契约（如启用）
├── versions/<version>/TECHNICAL_DESIGN.md  按需版本技术设计
├── versions/<version>/TEST_CASES.md 依据 PRD 的版本测试用例
├── engineering/SYSTEM_TECHNICAL_SPECIFICATION.md 当前完整技术事实
├── engineering/decisions/ADR-...    长期架构取舍
├── experiments/EXP-...              POC 证据与决定
├── delivery/RELEASE_PLAN.md         版本与发布计划
├── engineering/audits/...           独立审查结论
└── governance/lessons/...           可复用经验与源头规则索引
```

任务记录只保存关系和当前状态，不复制各文件正文。用户改变会影响后续工作的要求时更新任务记录；专业事实改变时更新对应 owner，并在任务记录中链接证据。

工作流任务中，Task Plan & Status Record 可以链接一个或多个 `run_id`；Run Manifest 反向记录 `task_id`。运行失败、重试或替代时更新运行 owner，只有跨阶段任务的整体边界、阶段或下一动作变化时才更新编号任务计划。

## 文件创建判断

创建项目前先依次判断：

1. 项目是否已有同一职责的权威文件或外部 issue／项目管理系统。
2. 该信息是任务状态、专业事实、运行状态、证据还是历史日志。
3. 能否更新现有 owner，而不是创建近义文件。
4. 新文件是否会被项目入口、项目地图、任务记录或专业文档发现。
5. 任务结束后该文件应继续现行、转为历史、归档还是删除。

编号计划文件、数据库或外部 issue 系统可以成为任务状态 owner；此时 `governance/tasks/` 只保存必要索引或完全不创建，但项目入口必须记录系统、对象 ID、状态语义和恢复方式。聊天内容不能作为唯一任务状态源。
