# 贡献 Senmu BuildOS

Senmu BuildOS 已从 `v1.0.0` 开始进入正式源码版本管理。任何变化都应维护清晰的职责边界、可执行性、按需加载和可验证交付。

## 修改原则

1. 先读取 `docs/architecture/skill-boundaries.md` 和当前任务对应的 Skill 入口。
2. 搜索是否已有同义规则、模板、脚本或 owner，优先完善现有实现。
3. 只有新主题无法自然归属时才新增 reference、资产、脚本或 Skill。
4. 不把客户信息、生产密钥、个人路径、项目私有 SOP 或单次故障细节写入通用产品能力。
5. 把完整 Git 仓库视为源码和版本边界；即使只修改一个 Skill，也要检查 README、架构、相邻 owner、Hooks、脚本、测试和发布元数据。
6. 应用项目经验先在应用项目内闭环，只有已经验证且能够跨项目复用的候选才进入 BuildOS。
7. 新增依赖、代码或内容时确认来源、许可证、维护责任和退出方式，不复制无法持续维护的材料。
8. 公开仓是由维护者的私有权威库生成的发布投影；贡献会先作为候选吸收到权威库，再经同一隐私门禁重新投影，因此最终提交可能被重写但会保留贡献归属。
9. 用外部网页、PDF、书、仓库或第三方 Skill 升级标准时，执行[工程知识蒸馏与标准晋级规范](skills/senmu-build-learning/references/工程知识蒸馏与标准晋级规范.md)；外部内容只作为临时候选，不把原文、来源目录或竞争规范直接装入运行时 Skill。

## 开放迭代飞轮贡献流程

你可以直接 `clone` 仓库做本地研究，也可以在 GitHub `fork` 后长期维护自己的 BuildOS。一次可回馈的改进使用一个范围清楚的短分支：

1. 从当前正式上游建立分支，声明本批主题、输入范围、目标 owner 和不执行边界。
2. 运行知识蒸馏流程，把外部材料转为候选规则卡；先搜索现有规则，逐条判定 `merge`、`replace`、`add`、`project_only`、`needs_evidence` 或 `discard`。
3. 只把可晋级语义写回现有唯一 owner；同步必要的路由、脚本、行为测试与变更记录，不提交原始资料库。
4. 运行本仓库完整验证，检查典型加载量和重复项；测试通过不能代替许可证、隐私、适用范围和语义裁决。
5. 在冻结的 Skill 行为表面上执行完整性复审，核对产品边界、路由、渐进披露、唯一 owner、重复／冲突、真实行为、Harness 兼容和授权边界；发现问题后回到原 owner 整改并复核。
6. 提交 Pull Request。维护者会把贡献重新视为候选进行审议，可能合并、改写、拆分、要求证据或拒绝；Pull Request 获接收不等于已经发布。

Pull Request 至少应说明：本批解决的决策缺口、实际读取范围、候选与处置摘要、修改的 owner、可观察行为差异、验证结果、上下文影响，以及来源许可证／隐私检查。未读取内容和未解决冲突必须明确标出。你可以永久保留自己的本地或 fork 版本，不需要为了使用 BuildOS 而向上游贡献。

## 验证

```bash
python3 scripts/validate_package.py
python3 scripts/validate_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

仓库 CI 复用这三组项目自有入口。修改 Skill 后还应运行 Skill Creator 的 `quick_validate.py`，并用 `tests/behavior/` 中的真实提示词做独立触发检查。格式通过不代表实际 Agent 路由、Hook 信任或任务行为已经验证。

## 正式版本准备

Senmu BuildOS 使用统一插件版本，不分别发布七个 Skill。先整理 `CHANGELOG.md` 的 `Unreleased` 内容，再使用项目自有入口准备下一个 SemVer 版本：

```bash
python3 scripts/bump_version.py 1.0.1 --date 2026-08-26 --dry-run
python3 scripts/bump_version.py 1.0.1 --date 2026-08-26
```

该脚本一次性更新 `VERSION`、`.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json` 的正式 Tag 指向和 Changelog 版本标题。它拒绝版本倒退、空的 Unreleased、现有版本漂移和非法日期，并在写入前完成全部解析；`--dry-run` 始终保持零写入。

准备完成后运行完整验证并审查差异：

```bash
python3 scripts/bump_version.py --check
python3 scripts/validate_package.py
python3 scripts/validate_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

版本准备、提交、Tag、GitHub Release 是不同状态。只有取得明确发布授权后，才提交版本变化并创建、推送对应的 `v<version>` Tag。Tag 工作流会核对 Tag 与仓库版本，重新运行全部测试和公开面门禁，再创建 GitHub Release；当前安装链直接消费 Git 源码，所以 GitHub 自动源码快照足够，不另造无消费者的定制制品。

## 高风险边界

插件安装、正式版本发布、GitHub Release、许可证变化和新平台兼容承诺属于独立决策，不因普通内容修改自动获得授权。
