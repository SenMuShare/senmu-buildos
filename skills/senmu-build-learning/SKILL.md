---
name: senmu-build-learning
description: "Distill external guidance and feedback into verified reusable learning. Use for the BuildOS feedback inbox, retrospectives, Lessons Learned, cross-project improvement, or absorbing a guide, book, repository, or Skill; not for raw feedback as rules, routine logs, or audits."
---

# Organizational Learning & Continual Improvement

让真实纠偏、返工和有效解法能够被捕获，又不让单次意见自动变成通用规则。原始反馈、经验候选、项目规则和 BuildOS 正式改进是四种状态，不得互相冒充。

面向用户先说结果与影响，再讲机制；首次出现的非通用缩写、状态名或符号用普通语言解释，技术深度匹配用户背景。

写入项目或 BuildOS 前，先确认权威项目根、Git 边界、专业规则 owner 和当前授权。Learning 面向完整项目事实链，不把单个 Skill、会话或发布单元天然当成项目边界。

## 路由

- 执行中的用户纠正、重复返工、规则冲突或临时绕行需要投递或集中处理：读取[反馈候选与集中审议规范](references/反馈候选与集中审议规范.md)。
- 已解决经验的复盘、项目 Lessons Learned 晋级、查重、替代和退役：读取[项目复盘与组织学习规范](references/AI复盘与治理闭环规范.md)。
- 将跨项目候选反哺到 Senmu BuildOS 源码项目：读取[BuildOS 项目演进与反哺规范](references/BuildOS项目演进与反哺规范.md)。
- 吸收网页、PDF、书、仓库、第三方 Skill 或工程手册：读取[工程知识蒸馏与标准晋级规范](references/工程知识蒸馏与标准晋级规范.md)。
- 在 clone／fork 中改进 BuildOS 或审议社区 Pull Request：同时读取上述两份规范；Learning 裁决知识，Delivery 管理分支、远端贡献与发布授权。

新增、修改、晋级、替代或退役正式 Lessons Learned 条目时，运行项目 policy 声明的经验校验命令；BuildOS 默认实例使用 `python3 .senmu-buildos/validate_lessons.py governance/lessons/LESSONS_LEARNED.md`。原始反馈候选不需要 Lessons ID 或 validator。

根因、结论或证据存在争议，或任务要求独立裁决时，组合 `senmu-build-assurance`。客户、用户和市场反馈先由 `senmu-build-product` 进入需求体系；只有已验证、会改变后续执行方式的部分才进入 Learning。

## 两段飞轮

1. **捕获**：`UserPromptSubmit` 捕获明确纠正或投递动作；Agent 发现可复用治理缺口时，在本地 CLI 可用的前提下静默提交。两者只写本机意见箱，不改项目规则、Skill 或发布状态；正常答复不显示内部标记或候选 ID。
2. **审议与晋级**：只在用户要求“处理／整理 BuildOS 意见箱”或同等任务时启动。查重、按根因聚类，再分为 `discard`、`project`、`buildos_candidate` 或 `needs_evidence`。
3. **反哺**：项目规则写回该项目的真正 owner；跨项目候选只在 BuildOS 源码仓取得修改授权后实施。安装、提交、推送和发布仍分别遵循实际授权。

## 晋级判断

- 出现次数是证据，不是机械门槛；一个严重机制缺口可以进入审议，多个项目私有问题也不当然通用。
- 候选要晋级，至少要有可复查事实、可判定触发信号、有效处置、适用范围和正确 owner。
- 稳定规则写回制造或控制问题的 Product、Workflow、Engineering、Delivery、Assurance 或 Project owner；Learning 只保留触发、证据和生命周期索引。
- 不为单次失误默认新增提示词、validator、审批或发布门禁；先修正问题生产源，只为重大剩余风险保留最小控制。
- 如果 BuildOS 已有正确规则但 Agent、项目脚本、validator 或发布入口仍产生相反行为，先修复真正的消费端、默认值或行为测试；不在多个 Skill 重复追加同义禁止句。
- 不把意见箱、工作日志、Lessons Learned 和专业规则写成四份同义正文；不反哺项目私有路径、客户数据、密钥或未公开事实。

## 输出

根据任务只给最小充分结果：反馈候选、审议分类、项目经验、源头规则或经授权的 BuildOS 整仓改进。明确证据、范围、状态、owner、未验证项和下次入口。
