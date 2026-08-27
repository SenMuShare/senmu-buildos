---
name: senmu-build-delivery
description: Govern non-routine Git or repository boundaries and formal version, artifact, deployment, rollback, or production-state decisions. Not for ordinary coding or a local commit that only records an engineering result.
---

# Delivery Management

确保提交、版本、制品、部署、生产事实和回滚属于同一发布／交付单元。普通本地 commit 不触发本 Skill；只有分支／worktree 边界、跨仓协作、版本、制品、部署、回滚或生产核验成为当前结果时才继续。

## 按结果读取

- 分支、worktree、Hotfix、合并和多 AI Git 协作：读取 [代码管理与合并规范](references/代码管理与合并规范.md)。
- monorepo／multi-repo、私有权威与公开投影、仓库拆分或发布单元：读取 [仓库边界与发布单元治理规范](references/仓库边界与发布单元治理规范.md)。
- 已发生工作的 Work Log、版本日志或交付接力：读取 [协作日志与版本日志规范](references/协作日志与版本日志规范.md)。
- 版本、Tag、代码包和制品：读取 [版本制品与发布规范](references/版本制品与发布规范.md)。
- 发布授权、目标环境、生产事实、失败核账和回滚判定：读取 [发布授权与生产事实协议](references/发布授权与生产事实协议.md)。
- 部署文档、安全、敏感信息和发布后核对：仅在这些事项进入当前范围时读取 [部署测试与安全规范](references/部署测试与安全规范.md)。

只读建议不执行合并、清理、Tag、上传、部署、切流或通知。项目已有发布规则和真实命令时优先使用，不为重述 BuildOS 加载额外 reference。

## 核心契约

- 先确认权威工作目录、用户改动、仓库／发布单元、目标环境、当前授权和可恢复点。
- Remote、PR、CI 和 Release 按项目现状启用；没有 Remote 不是治理缺陷。
- 分支、worktree 和并行目录只服务真实隔离或协作需要；不得因“创建分支”推导出第二工作目录。
- 版本、commit、Tag、制品、部署记录和生产验证必须对应；不适用层级不得伪造。
- 候选、已构建、已部署、已发布和生产可用分别登记；工具成功或 Tag 不能证明上线。
- 改变用户行为的候选必须回指已确认产品决定；高风险变更保持 fail closed。
- 发布前冻结当前 head 和匹配证据；新 commit 使旧批准失效。
- 正式发布保留可执行回滚点；未获得明确发布授权时，最多做到本地候选和预检。

需要修改实现时把失败证据和复核条件交 Engineering；需求范围不明交 Product；流程状态错误交 Workflow。Delivery 保留发布事实和授权边界，不复制其他 owner 正文。
