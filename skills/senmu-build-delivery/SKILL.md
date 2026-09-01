---
name: senmu-build-delivery
description: Govern development batches, non-routine Git, repository and release units, artifacts, deployment, rollback, and production state. Not for ordinary implementation.
---

# Delivery Management

把产品语言翻译成安全的 Git 与发布动作，保持版本、制品、生产事实和回滚一致。普通本地 commit 不触发。

## 按结果读取

- 开放批次、分支／worktree、Hotfix、合并、多 AI Git 协作或发布收口：读取 [代码管理与合并规范](references/代码管理与合并规范.md)。
- 多会话没有固定 Team Leader、需要防漏收口，或当前线与继任线并行：读取 [多 Agent 变更单元与版本线收口规范](references/多Agent变更单元与版本线收口规范.md)。
- monorepo／multi-repo、私有权威／公开投影、仓库拆分或发布单元：读取 [仓库边界与发布单元治理规范](references/仓库边界与发布单元治理规范.md)。
- 已发生工作的 Work Log、版本日志或交付接力：读取 [协作日志与版本日志规范](references/协作日志与版本日志规范.md)。
- 版本、Tag、代码包和制品：读取 [版本制品与发布规范](references/版本制品与发布规范.md)。
- 发布授权、目标环境、生产事实、失败核账和回滚判定：读取 [发布授权与生产事实协议](references/发布授权与生产事实协议.md)。
- 部署、安全、敏感信息或发布后核对：按需读取 [部署测试与安全规范](references/部署测试与安全规范.md)。

只读建议不合并、Tag 或部署。项目标准发布入口须机器可执行；分散脚本／文档清单不算流水线。标准发布不加载 Assurance，争议或硬门禁除外。

## 核心契约

- 从项目 owner、Git 和上下文恢复权威根、版本线、开放批次、发布单元、授权和恢复点。能推断时直接执行；只有会改变版本、批次或外部结果的歧义才确认。
- 同一版本、验收和发布／回退边界复用 `in_progress` 单元；真实并行才隔离。禁止写集成线、复用 sealed 单元或隐式串联任务分支。
- 换 Agent、换会话或重跑实验不改变 Change Unit；续作恢复原执行面。发布收口使用逐项留证、可中断恢复的 Release Control，不靠聊天记忆或口头“已完成”。
- 单项完成不等于批次完成。确认提测／收口后才冻结候选并运行集中门禁；明确发布后才进入制品、部署、生产验证和正式 Tag。
- 项目声明 `main` 为 `integration` 或 `release_ready`，否则停止自动集成；真实依赖仅可 stacked 到 sealed 父单元。职责不绑定会话或固定 Team Leader。
- 发布窗口只有一个可变源；截止后无关分支不改候选，Tag／制品前运行 [身份校验](scripts/verify_release_identity.py)。
- 分开登记候选、构建、部署、生产验证和版本；发布事实成立后才创建 Tag，并保留可执行回滚点。
- 未表达发布意图默认不发布；“不要发布／先别上线”持续生效。行为变化须回指产品决定，新 commit 使旧批准失效。

实现或专项证据未闭合交 Engineering；范围不明交 Product；流程状态错误交 Workflow。Delivery 不复制其他 owner 正文。
