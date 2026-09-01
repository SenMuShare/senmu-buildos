---
name: senmu-build-engineering
description: Govern architecture, engineering contracts, implementation review, testing strategy, technical debt, or refactoring when project rules are missing or changing. Not for routine fixes, visual or interaction direction or prototype validation, or ordinary implementation under clear project rules.
---

# Software Engineering

先核验项目入口、代码、配置、测试和真实命令。规则足够时交还项目；只在工程契约缺失、冲突、变化或明确要求治理时继续。

## 按结果读取

- 代码质量、缺陷闭环、AI 协作或评审：读取 [源代码工程质量与 AI 协作规范](references/源代码工程质量与AI协作规范.md)。
- 技术路线、框架、组件或方案判断：读取 [技术路线与组件选型](references/技术路线与组件选型.md)。
- 最小正确实现、复用或过度工程：读取 [实现经济性与过度工程治理规范](references/实现经济性与过度工程治理规范.md)。
- 架构边界、依赖、变更预算或技术债：读取 [架构约束与技术债治理规范](references/架构约束与技术债治理规范.md)。
- 前端状态、导航、数据、表单、响应式或浏览器验证：读取 [前端工程契约与验证规范](references/前端工程契约与验证规范.md)。
- API、服务、数据、事务、缓存、队列或后台任务：读取 [后端服务与数据契约规范](references/后端服务与数据契约规范.md)。
- 测试策略、替身、真实依赖、数据或 flaky：读取 [软件测试与质量验证规范](references/软件测试与质量验证规范.md)。
- 源码级重构或技术栈升级：读取 [源码级重构与技术栈升级规范](references/源码级重构与技术栈升级规范.md)。
- 从成熟代码库提炼项目规范：读取 [项目工程规范发现方法](references/项目工程规范发现方法.md)。
- 项目缺少规则或明确要求规范审查时，才按实际栈读取 [Python](references/Python工程编码规范.md)、[TypeScript](references/TypeScript工程编码规范.md)、[Go](references/Go工程编码规范.md)、[Java](references/Java工程编码规范.md)、[Ant Design](references/frontend-ant-design-practice.md) 或 [HTML／daisyUI](references/frontend-html-daisyui-practice.md)。

只读命中的 reference，语言 Profile 不连带。前后端是按需 Reference，不是父子 Skill 或岗位映射；专项 Skill 保持平级。

## 快速通道

单 owner、本地可逆且保持契约的 G1 局部变更由 Engineering 主责，不组合其他 Skill 或新增 PRD、ADR、Changelog。仍遵守 Kernel 的隔离、匹配验证和本地 commit。

开放批次单项只做必要检查；提测后才按冻结影响面集中验证。

安全、隐私、权限、支付、生产数据、付费、破坏性操作和正式发布不走快速通道。

## 核心契约

- 固定原始现象和调用链，先搜索项目 owner 与公开能力；新证据指向相邻依赖时才扩围或自建。
- 小改直接实现；长期改变公共契约、数据、基础设施或发布边界才建立 TD／ADR／POC。用户行为或验收变化先回 Product。
- 修复后先复跑原路径，再按影响回归；未覆盖原现象只声明部分验证，不靠放宽类型、测试或安全控制换取通过。

职责变化才交接给 Product、Design、Assurance、Delivery 或 Learning；只传事实、范围、证据、未决问题和授权边界。
