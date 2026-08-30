---
name: senmu-build-delivery
description: Govern non-routine Git or repository boundaries and formal version, artifact, deployment, rollback, or production-state decisions. Not for ordinary coding or a local commit that only records an engineering result.
---

# Delivery Management

把用户的产品语言翻译成安全的 Git 与发布动作，并使版本、制品、部署、生产事实和回滚一致。普通本地 commit 不触发本 Skill。

## 按结果读取

- 分支、worktree、Hotfix、合并、多 AI Git 协作，或用户用自然语言要求“并行修几个问题／把最新改动一起发布”：读取 [代码管理与合并规范](references/代码管理与合并规范.md)。
- 多会话没有固定 Team Leader、需要防漏收口，或当前线与继任线并行：读取 [多 Agent 变更单元与版本线收口规范](references/多Agent变更单元与版本线收口规范.md)。
- monorepo／multi-repo、私有权威与公开投影、仓库拆分或发布单元：读取 [仓库边界与发布单元治理规范](references/仓库边界与发布单元治理规范.md)。
- 已发生工作的 Work Log、版本日志或交付接力：读取 [协作日志与版本日志规范](references/协作日志与版本日志规范.md)。
- 版本、Tag、代码包和制品：读取 [版本制品与发布规范](references/版本制品与发布规范.md)。
- 发布授权、目标环境、生产事实、失败核账和回滚判定：读取 [发布授权与生产事实协议](references/发布授权与生产事实协议.md)。
- 部署文档、安全、敏感信息和发布后核对：仅在这些事项进入当前范围时读取 [部署测试与安全规范](references/部署测试与安全规范.md)。

只读建议不执行合并、Tag 或部署。优先项目真实入口；标准入口必须机器可执行，分散脚本／文档清单不算流水线。标准发布不加载 Assurance，争议或硬门禁除外。

## 核心契约

- 先确认权威目录、用户改动、发布单元、目标环境、授权和恢复点。
- 用户只表达当前线、后继线、这一批、是否集成和是否发布；Delivery 自动翻译 Git 机制。只读不创建执行面；每次源码写入进入任务分支，未知并行时再用独立 worktree，禁止直接写项目登记的集成线。
- 发布单元、环境和标准入口明确时，“发布最新版本”开启绑定精确候选的有限发布会话，自动完成适用的收口、制品、部署、验证和正式 Tag。
- 职责绑定动作而非会话身份：普通发布由当前 Agent 收口；仅跨多 Agent、仓库或生产单元的正式发布临时集中候选、授权和回执，不设固定 Team Leader。
- 项目必须声明 `main` 是 `integration` 还是 `release_ready`；未声明时停止自动集成。写入任务按版本线和 Change Unit 隔离，任务分支从登记集成线建立，只有已 sealed 的真实依赖可显式 stacked。
- 发布窗口只有一个可变源；截止后无关分支不改候选，Tag／制品前运行 [身份校验](scripts/verify_release_identity.py)。
- 候选、已构建、已部署、生产已验证和正式版本分别登记；正式 Tag 只在目标发布事实验证后创建，Tag 本身仍不能替代 Release Record 或生产事实。
- “不要发布／先别上线”是持久授权约束，必须写回项目现有 owner；它不阻止本地开发或集成，但不会因换会话、重试或形成新 commit 自动失效。
- 改变用户行为的候选必须回指产品决定；新 commit 使旧批准失效。
- 正式发布保留可执行回滚点；未获得明确发布授权时，最多做到本地候选和预检。

需要修改实现或专项证据未闭合时交 Engineering；需求范围不明交 Product；流程状态错误交 Workflow。Delivery 保留发布事实和授权边界，不复制其他 owner 正文。
