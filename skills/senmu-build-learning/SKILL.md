---
name: senmu-build-learning
description: Review the BuildOS feedback inbox, run a formal retrospective, promote verified lessons, or distill external guidance into reusable rules. Not for ordinary user corrections, routine logs, or independent audits.
---

# Organizational Learning

把原始反馈、候选经验、项目规则和 BuildOS 正式规则保持为不同状态。普通纠正先解决当前请求；只有用户要求审议意见箱、正式复盘、经验晋级或知识蒸馏时才加载本 Skill。

## 按结果读取

- 投递或集中处理反馈候选：读取 [反馈候选与集中审议规范](references/反馈候选与集中审议规范.md)。
- 已解决经验的复盘、查重、晋级或退役：读取 [项目复盘与组织学习规范](references/AI复盘与治理闭环规范.md)。
- 将跨项目候选改进到 BuildOS：读取 [BuildOS 项目演进与反哺规范](references/BuildOS项目演进与反哺规范.md)。
- 吸收网页、书、仓库、第三方 Skill 或工程手册：读取 [工程知识蒸馏与标准晋级规范](references/工程知识蒸馏与标准晋级规范.md)。

修改正式 Lessons Learned 时运行项目声明的校验命令；原始反馈候选不需要 Lessons ID。

## 核心契约

1. **捕获**：Hook 或 Agent 只写本机候选，不改变项目规则、BuildOS 或发布状态。
2. **审议**：按根因查重并分类为 `discard`、`project`、`buildos_candidate` 或 `needs_evidence`。
3. **晋级**：项目私有规则回到项目 owner；跨项目规则只有在证据、适用范围、处置方式和权威 owner 明确后才进入 BuildOS。

出现次数不是机械门槛。先修正制造问题的源头；不为单次失误默认新增提示词、validator 或审批，也不在多个 Skill 追加同义规则。意见箱、Work Log、Lessons Learned 和专业规则不得保存四份同义正文。

事实或根因存在争议时交 Assurance；客户需求先进入 Product。Learning 只裁决知识生命周期，不接管专业事实或 Git／发布授权。
