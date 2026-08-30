---
name: senmu-build-product
description: Create or change durable product scope, requirements, prioritization, roadmap, acceptance criteria, or product-state decisions. Not for ordinary request clarification, technical design, deployment, or presentation changes that preserve the product contract.
---

# Product Management

维护从可选用户需求、每版本 PRD 到当前产品规格书和验收的单一产品事实链。只有持久产品契约需要建立或改变时才继续；普通实现澄清、技术选择和保持产品语义的表现层调整不触发本 Skill。

读取 [需求与产品迭代管理规范](references/需求与产品迭代管理规范.md) 判断文档流转、owner、冻结与回写。真正创建文档时再读取对应模板，不从 Reference 重新拼装内容结构：

- 零散想法：[用户需求模板](assets/product-governance/USER_REQUIREMENTS.template.md)
- 开发版本：[产品需求文档模板](assets/product-governance/PRD.template.md)
- 当前产品全貌：[产品规格书模板](assets/product-governance/PRODUCT_SPECIFICATION.template.md)

低风险讨论可直接给出判断，不为展示完整流程而读取 Reference、模板或生成文档。

## 核心契约

- 用户决定目标、偏好和授权，但引导性问题、现状判断和候选方案不自动成为事实或正式需求。
- 先区分当前事实、期望状态、假设和建议；需要外部资料时说明它不能替代项目事实。
- 目录和文档职责提供稳定默认值；模板负责内容骨架。模板中的“必要”只对已经决定创建的那份文档生效，“按需”内容不适用就删除，不生成空章节或无意义台账。
- 用户需求池可选；每版本 PRD 定义本次开发与验收，产品规格书只保存当前完整产品事实。关联状态直接写在需求旁，不另建关系表。
- 投入大、证据薄或方向不确定时比较不做、复用／购买和最小方案；低成本可逆调整不强制完整发现流程。
- 状态型、编辑型、多入口或跨视图能力，只记录会改变验收的生效、持久化、失败、退出、刷新、切换、草稿和恢复语义。
- 产品契约未变时，表现层等价变更由实现 owner 和匹配验证承载，不修改 PRD。
- 需求生命周期、迭代承诺、实现完成、产品验收和真实发布分别登记；不得互相冒充。
- 进入实现的需求建立稳定 ID，并关联 PRD、任务、实现、测试、验收和发布证据。

技术路线交 Engineering，版本／生产事实交 Delivery，项目权威冲突交 Project，可复用经验交 Learning。跨阶段工作沿用项目现有任务 owner，不建立第二套状态或产品文档。
