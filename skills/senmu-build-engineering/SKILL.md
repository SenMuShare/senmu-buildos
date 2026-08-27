---
name: senmu-build-engineering
description: Govern technical decisions, architecture, implementation, testing, refactoring, dependencies, and technical debt for software, scripts, and code-bearing workflows. Use when the result is a technical design, code change, defect fix, test strategy, or engineering baseline; not for independent audits, product prioritization, release approval, or project-wide governance mapping.
---

# Software Engineering

技术质量连接需求、架构、实现和验证；复杂度只服务已知需求与质量属性。

先说结果；术语用白话。

写入项目产物前，先读项目入口并复用现有语义 owner。BuildOS 默认模板只用于新初始化实例；成熟项目须先映射并获授权，禁止创建默认目录或平行事实源。

## 按结果读取

- 日常源码质量、职责、错误、副作用、缺陷闭环、AI 协作和评审：读取 [源代码工程质量与 AI 协作规范](references/源代码工程质量与AI协作规范.md)。
- 技术判断、当前系统事实核验、技术路线、框架、组件和规划产物：读取 [技术路线与组件选型](references/技术路线与组件选型.md)。
- 最小正确实现、复用、语义契合和过度工程：读取 [实现经济性与过度工程治理规范](references/实现经济性与过度工程治理规范.md)。
- 模块边界、依赖方向、架构契约、变更预算和技术债：读取 [架构约束与技术债治理规范](references/架构约束与技术债治理规范.md)。
- 测试策略、层级、替身／真实依赖、数据、flaky 和质量证据：读取 [软件测试与质量验证规范](references/软件测试与质量验证规范.md)。
- 源码级重构或技术栈升级：读取 [源码级重构与技术栈升级规范](references/源码级重构与技术栈升级规范.md)。
- 从成熟代码库提炼项目工程规范：读取 [项目工程规范发现方法](references/项目工程规范发现方法.md)。
- 语言／框架：按代码读取 [Python](references/Python工程编码规范.md)、[TypeScript](references/TypeScript工程编码规范.md)、[Go](references/Go工程编码规范.md)、[Java](references/Java工程编码规范.md)、[Ant Design](references/frontend-ant-design-practice.md) 或 [HTML／daisyUI](references/frontend-html-daisyui-practice.md) 专项。

只加载当前决策所需 reference；语言 Profile 不连带。新项目按需使用 [engineering-governance assets](assets/engineering-governance/) 和 [architecture-governance assets](assets/architecture-governance/)；Project 不复制模板。

## 判断与核验

用户目标不决定工程事实。现状先核验；不支持时直说，未核验时作条件判断。方法见[技术路线与组件选型](references/技术路线与组件选型.md)。

## 实现契约

1. 修改前读取真实入口、需求／验收、调用链、测试、配置和项目本地规范；不从目录名或文档候选猜当前实现。
2. 确认需求语义、风险和质量属性，再搜索项目已有 owner、实现、平台原生能力、标准库、已安装依赖和成熟生态方案。候选“已存在”或“流行”都不等于满足契约。
3. 按影响选择最小规划产物：小改动直接实现；跨步骤／会话工作更新 Durable Task State；需要说明方案时建 TD；改变方案的未知项需独立证据时建 POC；长期改变公共契约、数据、基础设施或发布边界时建 ADR。
4. 优先扩展原 owner，以最小端到端价值切片闭合权威输入、真实核心路径、可观察结果、匹配验证和可交付输出。新模块必须有清晰职责、依赖方向和必要性，不让脚手架、抽象或门禁长期先于核心价值。
5. 复杂任务按可验证阶段推进，把有意义阶段的结果、证据、未完成项和下一步写回 Durable Task State；其他事实仍进入各自专业 owner。
6. 实现稳定后、最终评审前，对本次实质改动做有边界的复用、质量和效率简化；保持行为和安全边界，不以删行数、增加抽象或固定多 Agent 仪式作为成绩。

普通技术一致性由本 Skill 核对需求、设计／ADR、Task、实现和测试；一致追踪不等于归同一个 owner，各项仍回到专业 owner。只有独立结论、跨域争议或正式职责分离才交 Assurance；G3-G4 只提高验证强度。

## 缺陷、变更与证据

- 缺陷先区分 `confirmed`、`likely_unreproduced`、`expected_behavior`、`duplicate` 和 `out_of_scope`。能复现时先固定原始现象和入口；修复后同时运行原始复现和匹配回归。未覆盖原始现象时只能声明部分验证。
- 实现会改变用户动作、可见状态、生效／持久化、撤销／恢复、范围或验收时，先说明原行为、技术约束和保持行为的替代，交 Product 决策；内部机制不得变成未经确认的用户步骤。改变模块、接口、数据、依赖或长期路线时回写 TD／ADR，只改变执行顺序时更新 Task。
- 项目本地代码、架构和运行证据是当前事实权威，但既有做法不因存在就自动正确。发现重复 owner、结构缺陷或过时规则时，在授权内修正原 owner，不建平行体系。
- 未内置 Profile 的项目保留现有语言、框架、构建和运行基线；先应用通用层、项目工具配置和官方生态，不以个人偏好重写技术栈。
- 匹配验证与风险成比例；安全、数据、权限、支付和发布相关逻辑不得因“简单”而省略保护。接受的技术债必须记录影响、上限、偿还触发条件和 owner。

## 协作与交接

- 会改变范围、业务规则或验收的需求歧义交给 `senmu-build-product`，传递需求 ID、冲突事实、技术影响、选项和必须回答的问题。
- 独立只读审查、可复现 POC 或争议性因果交给 `senmu-build-assurance`，传递冻结目标、commit／环境、变更摘要、已运行验证和盲区；Assurance 不自动获得修复授权。
- 实现与匹配验证完成并进入版本、制品、部署或发布时交给 `senmu-build-delivery`，传递发布单元、commit、变更范围、测试证据、配置／迁移影响和残余风险。
- 已验证的工程经验和重复失败模式交给 `senmu-build-learning`；稳定工程规则仍回写本 Skill 对应 owner，不把项目私有路径、客户数据或临时故障写入通用规则。
