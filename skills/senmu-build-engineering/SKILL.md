---
name: senmu-build-engineering
description: Govern engineering contracts, architecture, technical debt, testing, or refactoring when project rules are missing, conflicting, or changing. Not for ordinary code changes already governed by active project instructions.
---

# Software Engineering

先核验项目入口、代码、配置、测试和真实命令。项目规则已充分约束普通实现或修复时，立即交还项目且不读取 BuildOS reference；只有工程契约缺失、冲突、变化或用户明确要求治理时才继续。

## 按结果读取

- 代码质量、缺陷闭环、AI 协作或评审：读取 [源代码工程质量与 AI 协作规范](references/源代码工程质量与AI协作规范.md)。
- 技术路线、框架、组件或方案判断：读取 [技术路线与组件选型](references/技术路线与组件选型.md)。
- 最小正确实现、复用或过度工程：读取 [实现经济性与过度工程治理规范](references/实现经济性与过度工程治理规范.md)。
- 架构边界、依赖、变更预算或技术债：读取 [架构约束与技术债治理规范](references/架构约束与技术债治理规范.md)。
- 测试策略、替身、真实依赖、数据或 flaky：读取 [软件测试与质量验证规范](references/软件测试与质量验证规范.md)。
- 源码级重构或技术栈升级：读取 [源码级重构与技术栈升级规范](references/源码级重构与技术栈升级规范.md)。
- 从成熟代码库提炼项目规范：读取 [项目工程规范发现方法](references/项目工程规范发现方法.md)。
- 只有项目缺少对应规则或任务明确要求规范审查时，才按实际语言／框架读取 [Python](references/Python工程编码规范.md)、[TypeScript](references/TypeScript工程编码规范.md)、[Go](references/Go工程编码规范.md)、[Java](references/Java工程编码规范.md)、[Ant Design](references/frontend-ant-design-practice.md) 或 [HTML／daisyUI](references/frontend-html-daisyui-practice.md)。

每次只读取当前判断所需 reference；语言 Profile 不连带。

## 快速通道

单 owner、本地可逆且保持产品、运行和交付契约的 G1 局部变更，由 Engineering 单独主责，不组合其他 BuildOS Skill，也不新增 PRD、ADR 或 Changelog。快速通道仍遵守 Kernel 的隔离、匹配验证与本地 commit 合同。是否保持契约按用户动作、可见状态、持久化、接口、数据、权限和发布边界判断，不按代码行数或具体 UI 对象判断。

安全、隐私、权限、支付、生产数据、外部付费、破坏性操作和正式发布不走快速通道。

## 核心契约

- 先在用户点名的系统、原始现象和真实调用链取证；只有新证据指向相邻依赖时才扩大范围。
- 先搜索项目既有 owner、框架公开 API、平台、标准库和依赖，再决定自建；现有能力须通过语义与风险门禁。绕过公开扩展点或依赖内部接口时读取《实现经济性》规范。
- 选择与影响相称的产物：小改直接实现；跨阶段更新现有任务状态；长期改变公共契约、数据、基础设施或发布边界才建立 TD／ADR／POC。
- 扩展原 owner，以最小端到端切片闭合输入、核心路径、可观察结果和匹配验证。
- 缺陷先固定原始现象与关键依赖形态；修复后先复跑原路径，再按影响扩大回归。未覆盖原现象只能声明部分验证。
- 会改变用户行为或验收的实现先回到 Product；纯内部机制不得变成未经确认的新用户步骤。
- 验证强度与风险相称；不得靠放宽类型、断言、测试或安全控制换取通过。
- 最终收口检查重复、职责、错误、副作用和资源浪费，但不以删行数或增加抽象为成绩。

职责发生变化时才交接：产品决定给 Product，独立裁决给 Assurance，版本／部署给 Delivery，可复用经验给 Learning。交接传递事实、范围、证据、未决问题和授权边界。
