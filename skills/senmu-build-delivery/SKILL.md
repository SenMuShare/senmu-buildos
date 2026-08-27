---
name: senmu-build-delivery
description: Govern Git collaboration, repository and release-unit boundaries, versions, artifacts, deployment, rollback, and production verification. Use when the result is a branch or merge decision, release candidate, formal release, rollback, or production-state verdict; not for ordinary coding, product prioritization, or workflow run state without a release concern.
---

# Delivery Management

确保提交、仓库、版本、制品、部署、线上状态和回滚依据属于同一个可追溯发布／交付单元。成功构建、单个接口可用或工具返回结果都不能单独证明正式发布完成。

面向用户先说结果与影响，再讲机制；首次出现的非通用缩写、状态名或符号用普通语言解释，技术深度匹配用户背景。

用户询问“应该怎么做”、“现在是否合理”或“怎么治理”时，先做只读现场判定，再给出适配当前项目的建议、理由、例外和收口条件；不把默认分支模型、目录或清单当成唯一答案。用户只要建议或审查时，不因给出建议而创建、合并、清理或发布。

交付初始化模板由本 Skill 唯一持有：需要建立分支、版本、部署、changelog 或发布规则时，使用 [delivery-governance assets](assets/delivery-governance/)，不要在 Project 下维护第二套发布模板。

写入项目产物前，先读项目入口并复用现有语义 owner。BuildOS 默认模板只用于新初始化实例；成熟项目须先映射并获授权，禁止创建默认目录或平行事实源。

## 路由

- 分支、提交、合并、worktree 和多 AI 代码协作：读取 [代码管理与合并规范](references/代码管理与合并规范.md)。
- monorepo／multi-repo、仓库拆分、私有权威到公开投影和发布单元：读取 [仓库边界与发布单元治理规范](references/仓库边界与发布单元治理规范.md)；项目采用白名单公开投影且已有 manifest 时，可先用 `scripts/export_public_projection.py` 规划，只有获得写入授权后才加 `--apply`。
- 需要把已经发生的交付工作追加到项目统一 Work Log，或维护版本日志与交付接力时：读取 [协作日志与版本日志规范](references/协作日志与版本日志规范.md)。本 Skill 不另建工作日志或经验台账。
- 版本、Tag、代码包、制品和发布收口：读取 [版本制品与发布规范](references/版本制品与发布规范.md)。
- 发布授权、候选状态、目标环境、生产事实、失败核账和回滚判定：读取 [发布授权与生产事实协议](references/发布授权与生产事实协议.md)。
- 部署文档、测试、安全、敏感信息和发布后核对：读取 [部署测试与安全规范](references/部署测试与安全规范.md)。

## 核心契约

- 修改和发布前确认权威工作目录、分支、用户已有改动和受影响发布单元。
- 本地 Git 是完整基础能力；Remote、PR／MR、CI 和 GitHub／GitLab Release 只按项目现状与明确授权启用，没有 Remote 不构成治理缺陷。
- 默认在一个权威目录内串行写入；用户只要求创建分支时不得推导为 worktree、clone 或第二个目录。额外 worktree 只用于获准的真实并行或环境隔离，登记位置并在权威主目录收口。
- 已声明会替换主线的继任版本线必须登记最终集成目标、Hotfix 前向传播契约和晋升条件。传播责任不等于立即打断开发：按适用性、风险和检查点决定同步时机，晋升前清零仍适用的待同步项；停留在旁路分支不算项目完成。
- 版本、changelog、提交、Tag 及本发布单元实际采用的制品、镜像、部署记录和目标验证必须彼此对应；不适用层级不得伪造。
- 正式发布保留可执行回滚点和恢复步骤；高风险变更 fail closed。
- 合并和发布前收口当前范围内的需求、技术、代码、测试、文档和日志，不夹带无关工作。
- 第一方代码进入集成基线前审查冻结变更集；批准绑定当前 head，新 commit 使旧批准失效。发布只核验该凭证，不等到发布才首次审代码。
- 改变用户行为的候选必须回指获确认的产品决定；同一实现分支把代码、文档和测试改成一致，只能证明内部一致，不能自行证明需求授权成立。
- 只报告实际验证过的状态，未发布必须保持未发布。
- “准备候选／预检”不授权 Tag、上传、SSH、部署、切流、通知或清理；外部变更只在用户明确授权的发布单元、环境和动作范围内执行。
- 正式部署项目应把“当前已验证版本＋一个已验证回滚版本”作为默认保留基线，并在唯一发布入口分别收口本机构建端、生产运行端和按需远程制品库；项目明确策略优先，但不得静默破坏回滚、数据或合规边界，也不使用跨项目全局 prune。
- Release Record 记录一次发布尝试；线上运行对象、版本接口和用户可见主流程共同构成生产事实，计划、Tag 或本地制品不能替代它。
- 收到明确发布命令的当前执行者承担当次收口职责，并从持久任务、Git 与发布记录恢复范围；职责不绑定固定 Agent 身份，也不替开发分支补找未提交事实。
- 多阶段合并、迁仓、发布或回滚任务使用项目声明的 Durable Task State Owner；采用 BuildOS 新项目默认实例时才写入 `governance/tasks/TASK-<NNNN>-<slug>.md`。版本、changelog、制品、部署记录和线上事实仍由各发布单元及交付文档负责。

## 协作与交接

- 版本范围或产品验收不明确时，向 `senmu-build-product` 交接候选需求、冲突状态、缺失验收和版本影响；需求是否进入版本由 Product 主责。
- 构建、测试、迁移或运行缺陷需要修改实现时，向 `senmu-build-engineering` 交接 release／commit、失败证据、环境差异、影响范围和复核条件；Delivery 保留发布记录和授权边界。
- 部署流程的 checkpoint、幂等、物料或回执契约有问题时，向 `senmu-build-workflow` 交接 run ID、步骤状态、输入输出身份和外部事实；工作流内部状态由 Workflow 主责。
- 已验证的交付经验和重复失败模式交给 `senmu-build-learning`；本 Skill 只向统一 Work Log 追加已发生的交付事实。
- 默认不执行部署、发布、外部通知或删除，除非用户授权范围明确。
