---
name: senmu-build-assurance
description: "Produce evidence-graded POC, audit, reproduction, or disputed-cause verdicts when an independent finding is the requested result. Not for implementation, routine technical judgment, retrospectives, or applying fixes."
---

# Governance Assurance

默认只读。冻结对象、版本、范围和标准后，以可复查证据区分事实、推断与未验证项；本 Skill 给出结论，不自动修复。

## 按结果读取

- 决策型 POC、盲测、对照实验、实验账本或复现：读取 [POC 可复现实验治理规范](references/POC可复现实验治理规范.md)。
- 代码、架构、治理、交付或全项目审查：读取 [独立审查与证据分级规范](references/独立审查与证据分级规范.md)。只有用户明确要求逐文件、逐函数或逐条现有注释时才使用其中的 `exhaustive_source`。

普通一致性自查由对应专业 Skill 完成；G3-G4 不自动触发 Assurance。需要工程评价标准时只读取命中的 Engineering reference，不加载整个 Engineering Skill。

## 核心契约

- 声明审查身份：independent、peer 或 evidence-based self-review；无法证明职责分离时不得称独立审查。
- 记录冻结目标、覆盖图、证据来源与时效、未覆盖范围和停止条件。
- 证据只支持其直接观察到的主张；静态检查、测试、生产事实和独立复核不得互相冒充。
- 对候选问题主动寻找反证，再给出状态、P0-P3、影响边界、最小整改目标和复核条件。
- `not_assessed`、`inconclusive`、`resolved_unverified` 与 `verified_resolved` 必须区分。
- 审查授权不包含修改、发布、删除或改变生产状态；整改回到对应专业 owner。

跨阶段审查沿用项目现有持久任务 owner。交接只传 finding、证据、范围、目标结果和复核条件，不复制专业规范。
