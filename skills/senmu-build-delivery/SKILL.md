---
name: senmu-build-delivery
description: Govern open development batches, non-routine Git or repository boundaries, version closeout, artifacts, deployment, rollback, or production state. Not for ordinary implementation inside an already-governed batch.
---

# Delivery Management

把产品语言翻译成安全的 Git 与发布动作，保持版本、制品、部署、生产事实和回滚一致。普通本地 commit 不触发。

## 按结果读取

- 开放开发批次、版本归属后的分支执行、worktree、Hotfix、合并、多 AI Git 协作或发布收口：读取 [代码管理与合并规范](references/代码管理与合并规范.md)。
- 多会话没有固定 Team Leader、需要防漏收口，或当前线与继任线并行：读取 [多 Agent 变更单元与版本线收口规范](references/多Agent变更单元与版本线收口规范.md)。
- monorepo／multi-repo、私有权威与公开投影、仓库拆分或发布单元：读取 [仓库边界与发布单元治理规范](references/仓库边界与发布单元治理规范.md)。
- 已发生工作的 Work Log、版本日志或交付接力：读取 [协作日志与版本日志规范](references/协作日志与版本日志规范.md)。
- 版本、Tag、代码包和制品：读取 [版本制品与发布规范](references/版本制品与发布规范.md)。
- 发布授权、目标环境、生产事实、失败核账和回滚判定：读取 [发布授权与生产事实协议](references/发布授权与生产事实协议.md)。
- 部署文档、安全、敏感信息和发布后核对：仅在这些事项进入当前范围时读取 [部署测试与安全规范](references/部署测试与安全规范.md)。

只读建议不合并、Tag 或部署。优先项目真实入口；标准入口须机器可执行，分散脚本／文档清单不算流水线。标准发布不加载 Assurance，争议或硬门禁除外。

## 核心契约

- 从项目 owner、Git 和上下文恢复权威目录、目标版本线、开放批次、发布单元、交付阶段、授权和恢复点。能推断版本与交付意图时直接执行；只有歧义会改变版本、批次或外部结果时才用产品语言确认一次。未表达发布意图默认不发布。
- 同一目标版本、共同验收和共同发布／回退边界内的连续需求复用当前 `in_progress` 单元；单一写入者不因每次补充另建分支或 worktree，真实并行再由 Delivery 内部隔离。禁止直接写项目登记的集成线或复用 sealed 单元。
- 单项实现完成不等于批次完成，不自动封口、合并、运行完整门禁或准备发布。负责人确认提测／收口后才冻结批次并集中形成候选；明确发布授权后才进入制品、部署、生产验证和正式 Tag。
- 职责绑定动作而非会话：普通发布由当前 Agent 收口；仅跨 Agent、仓库或生产单元的正式发布临时集中候选、授权和回执，不设固定 Team Leader。
- 项目必须声明 `main` 是 `integration` 还是 `release_ready`；未声明时停止自动集成。写入任务按版本线和 Change Unit 隔离，任务分支从登记集成线建立，仅 sealed 真实依赖可 stacked。
- 发布窗口只有一个可变源；截止后无关分支不改候选，Tag／制品前运行 [身份校验](scripts/verify_release_identity.py)。
- 分别登记候选、已构建、已部署、生产已验证和正式版本；只在目标发布事实成立后创建正式 Tag，Tag 不替代 Release Record 或生产事实。
- “不要发布／先别上线”是持久授权约束，必须写回项目现有 owner；未说明是否发布则保持未授权，不因换会话、重试、commit、测试或集成自动放行。
- 改变用户行为的候选必须回指产品决定；新 commit 使旧批准失效。
- 正式发布保留可执行回滚点。

修改实现或专项证据未闭合交 Engineering；需求范围不明交 Product；流程状态错误交 Workflow。Delivery 保留发布事实和授权边界，不复制其他 owner 正文。
