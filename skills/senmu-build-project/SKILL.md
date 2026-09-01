---
name: senmu-build-project
description: Create or repair project governance, authority mapping, structure, and durable cross-stage state. Not for routine work under an established project system.
---

# Project Management

负责项目治理实例、权威结构和跨领域 owner，不是其他 Skill 的父级。正常开发在项目入口足够时立即交还；只有治理入口缺失／冲突、结构演进、状态 owner 需要修复或明确要求治理时才继续。

## 按结果读取

- 创建、审视或演进治理实例：读取 [项目治理实例与演进规范](references/项目治理实例与演进规范.md)。
- 长期接管并分阶段治理成熟项目：读取 [成熟项目接管治理专项规范](references/成熟项目接管治理专项规范.md)。
- 广义生命周期、模块组合或完成定义：读取 [项目实践指南](references/项目实践指南.md)。
- 项目根、目录布局、文档 owner 或项目地图：读取 [项目目录与文档规范](references/项目目录与文档规范.md)。
- 从成熟项目发现真实规范或建立按需索引：读取 [项目规范发现与按需加载规范](references/项目规范发现与按需加载规范.md)。
- 创建、选择或修复跨阶段任务状态 owner：读取 [任务执行与状态管理规范](references/任务执行与状态管理规范.md)。
- 四类项目处境、项目移交或 Skill 调用边界：读取 [项目落地移交与场景路由规范](references/项目落地移交与场景路由规范.md)。
- 确实需要判断 G0-G4 或门禁强度时才读取 [治理强度分级与门禁规范](references/治理强度分级与门禁规范.md)。

只读取当前结果所需 reference。Git 执行由 Delivery 负责。

新项目用 [init_project_governance.py](scripts/init_project_governance.py)；成熟项目零写入盘点用 [assess_project_governance.py](scripts/assess_project_governance.py)。默认输出有界摘要；只有交付物需要完整候选与排除登记时才用 `--verbose`。脚本输出是事实候选，不替代语义确认、授权或运行验证。

## 核心契约

- 先确认权威根、Git／子项目／发布单元边界、入口、owner、授权和非目标。
- 单项放置问题只给首选 owner／路径和理由；用户没有要求写入时不创建文件。
- 新项目先用 `init_project_governance.py --mode plan-new` 生成零写入候选；只有明确授权后才 `initialize-new`。
- 成熟项目先用 `assess_project_governance.py` 做零写入盘点，再语义确认真实 owner；不得用默认模板覆盖或建立平行事实源。
- 结构按实际能力、生命周期和发布单元裁剪，不用项目类型替代事实或预建模块。
- 项目地图只导航 owner、入口、状态源和边界；根 `AGENTS.md` 只保存项目差异、真实命令和明确覆盖项。
- 跨阶段工作沿用唯一 Durable Task State Owner；使用既有任务系统不需要再次触发 Project。
- 初始化、迁移和整改分别授权；候选计划、脚本输出和静态校验都不是已执行事实。

只在 owner 变化时移交范围、入口、事实、证据、未决问题和授权边界，不复制专业正文。完成时核对没有平行 owner，并留下验证、风险和恢复入口。
