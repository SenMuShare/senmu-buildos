---
name: senmu-build-design
description: "Define, redesign, review, or repair UI/UX: visual direction, design systems, layout, typography, color, data visualization, responsive behavior, interaction, motion, accessibility, or interface prototypes. Not for product scope or copy, routine implementation under an approved design, library-specific APIs, or independent audits."
---

# Interface Design

把模糊审美、界面问题或体验目标转成项目可实现、可验证的设计决定。先读取真实页面、产品行为、现有设计系统、组件库、品牌资产和目标设备；项目已有设计 owner 时扩展它，不另建第二套视觉标准。

## 按结果读取

- 新页面、改版、跨页面视觉方向、设计系统、布局、字体、色彩、数据可视化、材质或响应式规则：读取[界面视觉与设计系统规范](references/界面视觉与设计系统规范.md)。
- 交互模式、状态反馈、手势、动效、可访问性或界面“手感”：读取[交互动效与可访问性规范](references/交互动效与可访问性规范.md)。
- 方向不确定，需要多个真实方案、交互原型或整体 UI/UX 评审：读取[原型探索与界面评审规范](references/原型探索与界面评审规范.md)。

只读取当前决定所需 reference。已有明确设计稿或项目规则下的普通实现直接按项目／Engineering 执行；Ant Design、shadcn、GSAP 等专项 Skill 只在需要其当前 API 或实现方法时使用，不复制到本 Skill。

## 核心契约

- 先确认界面类型、主要用户任务、使用环境、内容层级、现有资产和技术约束；不让用户先学设计术语。输入不足时给少量可理解且有实质差异的方向，并明确推荐、适用场景与风险。
- 设计决定必须能落实为层级、布局、组件、Token、状态、素材、响应式和验证条件；“高级、现代、科技感”本身不是规格。
- 复用项目设计系统、品牌和组件。只有跨页面稳定缺口才治理设计系统；一次性页面变化留在现有实现 owner，不创建平行 `MASTER`、清单或样式库。
- 视觉、交互和动效共同服务用户任务。高频操作优先直接、快速和可预测；动效须有反馈、状态、空间关系、解释或减少突变等目的，并提供减弱动效与非悬停输入的可用路径。
- 可访问性、响应式、加载／空／错／禁用等状态从设计开始，不作为交付前补丁。重要信息和操作不能只靠颜色、位置、图标、声音或运动表达。
- 评审基于真实渲染、目标视口、关键状态和可观察影响；代码存在或静态检查通过不能单独证明视觉质量、交互手感或设备可用性。
- 当前结果是探索时，原型与候选不冒充产品决定；选定后只把稳定规则写回项目现有设计／产品 owner，未选方案保持隔离并按授权清理。

产品范围、行为、界面内容和验收变化交 Product；技术架构、依赖和实现契约交 Engineering；需要独立证据结论交 Assurance；Git、版本和发布事实交 Delivery。
