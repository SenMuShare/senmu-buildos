---
name: senmu-build-product
description: Define durable product scope, version placement, priority, acceptance, state, and cross-page interface content. Not for one-off edits, implementation review, technical design, or deployment.
---

# Product Management

维护可选用户需求、每版本 PRD、当前产品规格和验收的单一事实链。持久契约、版本归属或跨页面内容标准变化时才继续。

## 按结果读取

- 产品需求、版本归属、文档流转、冻结与回写：读取 [需求与产品迭代管理规范](references/需求与产品迭代管理规范.md)。
- 跨页面按钮、状态、错误、术语或生成内容：读取 [界面文案与内容设计规范](references/界面文案与内容设计规范.md)，再只读目标语种的[中文规范](references/界面文案中文规范.md)或[英文规范](references/界面文案英文规范.md)。已有等价标准时只补缺口。

真正创建文档时才读取[用户需求](assets/product-governance/USER_REQUIREMENTS.template.md)、[版本 PRD](assets/product-governance/PRD.template.md)或[产品规格](assets/product-governance/PRODUCT_SPECIFICATION.template.md)模板，不从 Reference 重拼结构。

低风险讨论可直接给出判断，不为展示完整流程而读取 Reference、模板或生成文档。

## 核心契约

- 用户决定目标、偏好和授权；引导性问题、现状判断和候选方案不自动成为正式需求。
- Product 决定当前版本、后续版本或需求池；事实足够时不重复询问，只有归属会改变范围或时间且无法判断时才确认。版本遵循项目策略，不凭数字猜测。
- 跨页面界面语言由 Product 维护；项目术语、品牌语气和平台差异写入现有产品规格、设计系统或等价 owner，不新建平行文案台账。保持既有产品语义的单条改写由实现 owner 直接完成。
- 先区分当前事实、期望状态、假设和建议；需要外部资料时说明它不能替代项目事实。
- 模板只负责已决定创建的文档骨架；“按需”内容不适用就删除，不生成空章节或台账。
- 需求池可选；版本 PRD 定义开发与验收，产品规格只保存当前事实。状态写在需求旁，不另建关系表。
- 投入大、证据薄或方向不确定时比较不做、复用／购买和最小方案；低成本可逆调整不强制完整发现流程。
- 只记录会改变验收的生效、持久化、失败、退出、切换、草稿和恢复语义；契约未变的表现层调整不修改 PRD。
- 需求生命周期、迭代承诺、实现完成、产品验收和真实发布分别登记；不得互相冒充。
- 进入实现的需求建立稳定 ID，并关联 PRD、任务、实现、测试、验收和发布证据。

视觉方向、设计系统、交互、动效和 UI/UX 评审交 Design；技术路线交 Engineering，版本／生产事实交 Delivery，项目权威冲突交 Project，可复用经验交 Learning。跨阶段工作沿用项目现有任务 owner，不建立第二套状态或产品文档。
