---
name: senmu-build-assurance
description: "Produce evidence-graded verdicts for POCs, frozen-target audits, technical-debt baselines, and disputed causal claims. Use when the result is an independent comparison, reproduction, finding set, or remediation decision; not for implementation, ordinary technical selection, retrospectives, or applying fixes without separate authorization."
---

# Governance Assurance

以独立、可复现和可追踪的证据支持决策。默认只读，先区分已确认事实、推断和未验证状态，再给出问题级别、影响边界和后续选择。

面向用户先说结果与影响，再讲机制；首次出现的非通用缩写、状态名或符号用普通语言解释，技术深度匹配用户背景。

写入项目产物前，先读项目入口并复用现有语义 owner。BuildOS 默认模板只用于新初始化实例；成熟项目须先映射并获授权，禁止创建默认目录或平行事实源。

## 路由

- 决策型 POC、冻结输入、运行账本、盲测、保留和复现：读取 [POC 可复现实验治理规范](references/POC可复现实验治理规范.md)。
- 代码、架构、治理、交付或全项目审查的范围冻结、证据等级、P0-P3 和复核：读取 [独立审查与证据分级规范](references/独立审查与证据分级规范.md)。明确要求每个第一方源码文件、函数／方法和现有注释时，使用其 `exhaustive_source` 模式和可校验控制记录，不得退化为抽样。

普通需求或技术一致性自查分别由 Product／Engineering 主责，不触发本 Skill。只有用户明确要求独立结论、存在跨域争议，或正式审查确实需要职责分离时，Assurance 才成为主责。G3-G4 只提高证据、验证和收口强度，本身不自动触发 Assurance。

工程审查需要技术上下文时，读取 `senmu-build-engineering` 的架构、代码质量、实现经济性和技术债 owner，不复制其规则；工程审查任务模板也由该 Skill 的 `assets/architecture-governance/` 唯一持有。POC 账本和 manifest 位于本 Skill 的 `assets/poc-experiment-governance/`。审查或实验产生可复用经验时，把证据、适用范围和未验证项交给 `senmu-build-learning` 判断是否晋级。

## 协作与交接

- 审查前从相应专业 Skill 读取评价规则与事实 owner，但 Assurance 保持结论主责，不让被审查者替代证据裁决。
- 发现需要整改的问题时，只交接 finding ID、证据、影响范围、责任 owner、目标结果和复核条件；代码修复交给 `senmu-build-engineering`，产品范围修正交给 `senmu-build-product`，发布处置交给 `senmu-build-delivery`。只读审查本身不授权任何修改。
- 整改完成后，复核原冻结目标和验收条件，不因实施者声称完成就关闭 finding。
- 已验证且可复用的模式交给 `senmu-build-learning`，不把完整审查报告复制为经验条目。

## 核心契约

- 冻结问题、输入、环境、版本、命令和评价标准后再比较结果。
- 审查结果关联路径、运行状态、日志、测试或其他可复查证据。
- 声明实际覆盖范围、取样方法、证据时效和盲区；没有覆盖的领域使用 `not_assessed`，不默认为通过。
- 只有执行者与实现决策具有足够分离时才称“独立审查”；同一 Agent 自查应如实标为 evidence-based self-review。
- 区分缺陷、技术债、接受的限制、实验结论和治理缺口。
- 本 Skill 只提供证据和结论，不直接拥有经验台账或通用规则晋级。
- 不因审查发现问题就自动修改代码、数据、版本或生产状态。
- 跨模块、分阶段或跨会话的审查与实验使用项目声明的 Durable Task State Owner；采用 BuildOS 新项目默认实例时才写入 `governance/tasks/TASK-<NNNN>-<slug>.md`。最终报告、实验账本和证据仍写入对应专业 owner。

## 输出

根据任务提供最小充分结果：POC 账本与结论、P0-P3 审查发现、技术债基线、因果证据、分阶段整改建议或复核条件，并明确证据等级、结论状态、残余风险和未验证项。
