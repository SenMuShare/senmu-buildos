---
name: senmu-build-project
description: "Recommend, plan, create, assess, or evolve project governance when the result is document or directory placement, canonical authority, owner mapping, a project map, governance profile, or durable cross-stage task state. Use for project start, structural cleanup, authority conflicts, or project-wide continuity; not routine single-domain work or independent audits."
---

# Project Management

负责项目启动、权威结构、治理强度、持久任务状态和责任边界；不是专业 Skill 的父级或单领域日常入口。

先说结果，再讲机制；术语首次出现时解释。

写入前先读项目入口并复用现有 owner。BuildOS 默认模板只用于新实例；成熟项目须先映射并获授权，禁止创建默认目录或平行事实源。

## 按结果读取

- 新建、审视或演进治理实例：读取 [项目治理实例与演进规范](references/项目治理实例与演进规范.md)。
- 长时间接管、审计并分阶段改造历史混乱的已有项目：读取 [成熟项目接管治理专项规范](references/成熟项目接管治理专项规范.md)。
- 需要广义生命周期、模块组合或完成定义：读取 [项目实践指南](references/项目实践指南.md)。
- 规划项目根、物理布局、文档 owner、项目地图或权威版本：读取 [项目目录与文档规范](references/项目目录与文档规范.md)。
- 从成熟项目发现真实规范、建立短索引或控制按需读取：读取 [项目规范发现与按需加载规范](references/项目规范发现与按需加载规范.md)。
- 工作需要多个依赖步骤、阶段、Agent 或会话恢复：读取 [任务执行与状态管理规范](references/任务执行与状态管理规范.md)。
- 处理项目内移交、场景路由或日常调用边界：读取 [项目落地移交与场景路由规范](references/项目落地移交与场景路由规范.md)。
- 判断 G0-G4、Hard Gate 或剩余风险：读取 [治理强度分级与门禁规范](references/治理强度分级与门禁规范.md)。

只读结果必需的 reference。

## 入场与实例契约

1. 读取项目入口、当前状态、真实目录／运行证据和项目本地规则。
2. 确认交付物是否真的包含治理实例、跨阶段状态或多领域责任边界；单领域结果直接由对应专业 Skill 主责。
3. 锁定权威项目根、受影响发布／交付单元、范围、非目标、授权、可逆性和 G0-G4；分别判断治理档位、公开模型、发布渠道、已确认制品和路径角色，不用项目类型或 `release` 档位替代这些事实。
4. 只组合当前结果跨越的专业职责，并在对应决策点读取所需 reference。

## 建议、规划与实施

指导或审视时，先报告现状、owner 和未确认项，再给方案、理由、风险与收口条件。普通问题不生成额外目录或状态系统。Git 执行面交 `senmu-build-delivery`。

- **单项放置建议**：用户只问文档或目录放在哪里时，读取当前入口、Project Map 和相关专业 owner，给出首选 owner／路径、理由、可接受替代和是否值得新建目录；不创建文件。用户明确要求“新建并放到合适位置”时，才在确认的现有 owner 中写入。
- **空白项目规划**：先依据需求、预期架构、安装／部署／交付方式明确工作对象、生命周期意图、组合方式、公开模型、发布渠道、已确认制品、G0-G4、core／standard／release 和实际模块。使用 `scripts/init_project_governance.py --mode plan-new` 输出零写入候选；推荐结构是可解释起点，不是强制答案，未确认能力不预建目录。
- **空白项目初始化**：用户明确要求创建或初始化后，使用已审阅的同组显式参数运行 `--mode initialize-new`。不得依赖隐含项目类型或档位；可用 `--modules` 覆盖类型推荐。若确认路径不同于脚本预设，不得为使用脚本而改回预设，应按目标地图建立最小 owner 并校准 policy。`--with-agents` 只用于项目自有 Agent，`--commit-baseline` 只提交校验通过的初始化文件且不创建 Tag。完成前校准占位字段并运行 validator。
- **成熟项目整理或迁移**：先用 `assess_project_governance.py` 零写入盘点，再语义确认真实 owner，并根据当前需求、架构与发布事实重新评估能力。先交付现状地图、目标地图、保留／新增／合并／移动项、迁移影响、兼容与恢复点；只有用户授权实施后才更新原 owner。脚本候选、建议和迁移方案都不是已执行事实。
- **成熟项目专项接管**：跨领域、多波或跨会话时建立唯一恢复入口，先只读冻结基线与 Finding，用户裁决后才由专业 owner 整改。未复核阻断项、最终复核或临时内容去留不得标记完成。

## 最小事实链

- 唯一权威项目根，以及 Git／worktree、子项目、外部工作区、legacy 和发布／交付单元边界。
- 工作对象、生命周期意图、交付模式、组合方式和 G0-G4；不用单一 `project_type` 掩盖其他维度。
- standard／release 新项目的短 `governance/PROJECT_MAP.md` 和 `.senmu-buildos/config.json`；地图只导航 owner、入口、状态源和边界，不复制专业正文或当前状态。
- 多步骤、跨阶段、跨 Agent 或跨会话工作的唯一 Durable Task State Owner。`governance/tasks/` 只是 standard／release 新项目默认实现；core 和成熟项目可沿用可信 README、Issue、任务包、数据库或外部系统。
- 只在启用 Agent 治理时建立 Agent Register、稳定定义和 Workflow／Harness 关联；根 `AGENTS.md` 仍只是 Codex 读取顺序入口。

## 协作与完成

只在职责切换时移交：Product 负责需求与验收；Workflow 负责流程与运行；Engineering 负责技术与代码；Delivery 负责 Git 与发布；Assurance 负责 POC 与独立审查；Learning 负责经验生命周期。

移交只传递任务标识、当前阶段、范围／非目标、权威入口、已确认事实与证据、未决问题、下一项结果和仍有效的授权边界；不复制专业规范正文。

完成前确认：没有建立平行 owner；源输入、实现、运行状态、中间物、交付物、证据和归档可区分；项目本地事实与当前状态一致；匹配验证已运行；未验证项、残余风险和恢复／交接入口已留下。安全、隐私、支付、权限、生产数据、破坏性操作和发布完整性的必要门禁仍 fail closed。
