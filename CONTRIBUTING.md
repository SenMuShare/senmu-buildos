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
8. 产品源码只有一份，按可公开标准维护；原始反馈、作者私有任务和未公开证据留在产品之外。公开贡献按正常候选审议接收，保留贡献归属；私有工作区的历史不推送到公开仓库。
9. 用外部网页、PDF、书、仓库或第三方 Skill 升级标准时，执行[工程知识蒸馏与标准晋级规范](skills/senmu-build-learning/references/engineering-knowledge-distillation-and-standard-promotion.md)；外部内容只作为临时候选，不把原文、来源目录或竞争规范直接装入运行时 Skill。

<a id="github-readme-sync"></a>
## GitHub 更新与三语 README

每个准备同步到 GitHub 的完整变更批次（包括仅同步源码、修复、文档更新和正式发布），都应结合实际差异审阅 `README.md`、`README.en.md`、`README.ja.md`，判断是否影响用户可见说明。检查定位、能力边界、工作方式、使用示例、安装／升级／卸载入口、版本摘要及相关链接；不把版本号替换当作内容审阅。

受影响的内容在同一批次中按三种语言同步，保持事实、约束、链接和使用含义一致，不要求逐句直译。未受影响的段落保留；完全没有 README 影响时，在已有 PR 或任务记录中简述原因，不为获得“已更新”状态机械改写。复用仍有效的审阅判断，后续只补看变化部分，不为每个本地提交新增审批、台账或强制全量阅读。

普通源码同步不自动创建新版本或发布记录。已授权的正式发布同时维护 `CHANGELOG.md`、`RELEASE_NOTES.md`、版本清单及三语摘要，复用下述原有版本准备与产品表面检查。源码版本、私有发布、公开渠道可用版本和本地安装是不同事实；不以其中一个状态宣称其他状态已经完成。

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

公开 clone／fork 使用公开包入口：

```bash
python3 scripts/validate_package.py
python3 scripts/validate_public_surface.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

维护者与外部贡献者运行同一套产品检查。产品可独立测试，不需要作者私有任务、实例配置或发布脚本；维护工具由维护工作区另行验证。

仓库 CI 复用公开包入口。修改 Skill 后还应运行 Skill Creator 的 `quick_validate.py`，并用 `tests/behavior/` 中的真实提示词做独立触发检查。格式通过不代表实际 Agent 路由、Hook 信任或任务行为已经验证。

## 正式版本准备

Senmu BuildOS 使用统一插件版本，不分别发布八个 Skill。先整理 `CHANGELOG.md` 的 `Unreleased` 内容，再使用项目自有入口准备下一个 SemVer 版本：

```bash
python3 scripts/bump_version.py 1.0.1 --date 2026-08-26 --dry-run
python3 scripts/bump_version.py 1.0.1 --date 2026-08-26
```

该脚本一次性更新 `VERSION`、Codex／Claude Code／ZCode 三份插件清单、两份 marketplace 清单、三语 README 的当前源码版本和 Changelog 版本标题；README 正文、三语摘要与用户更新说明仍需按实际变化编写。它拒绝版本倒退、空的 Unreleased、现有版本漂移和非法日期，并在写入前完成全部解析；`--dry-run` 始终保持零写入。

准备完成后运行完整验证并审查差异：

```bash
python3 scripts/bump_version.py --check
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/hooks/*.test.js
```

每个正式版本还必须在 `RELEASE_NOTES.md` 中维护简短的用户更新说明，只保留“主要更新”和“修复问题”两个栏目。内容描述用户最终得到的变化，不写任务编号、参考来源、内部讨论、验证过程或未公开计划。Tag 发布流程会读取对应版本段落作为 GitHub Release 正文；缺少任一栏目时停止创建 Release。

每个正式版本同时必须复审 GitHub 产品表面，而不是只机械修改版本号：

- 中文、英文、日文 README 同步审阅定位、核心问题、工作方式、设计理念、能力边界和安装入口；本次能力改变相关叙事时更新正文，没有叙事变化也要记录已经复核的栏目。
- `GITHUB_PRODUCT_SURFACE.json` 的 `reviewed_for_version` 必须与 `VERSION` 一致，并记录本次 README 复核栏目、三语摘要、仓库简介和不超过 20 个 Topics。
- README 中的 `product-surface-review` 标记必须与当前版本一致；它只是复核收据，不能代替真实内容更新。
- 仓库简介和 Topics 描述当前产品价值与发现关键词，不记录内部任务、参考 Skill、实现过程或夸大的效果承诺。

`validate_package.py` 会阻断缺少 Release 正文、README 三语复核或 GitHub Product Surface 漂移的候选。公开 `main` 精确校验成功后，`promote-public-release` 在创建 Tag 前同步并回读 GitHub 仓库简介与 Topics；同步失败时不创建正式 Tag。Tag workflow 必须最终创建非 draft、非 prerelease 的 GitHub Release，发布回执再核对其正文与 `RELEASE_NOTES.md` 一致。

版本准备、候选 commit、公开主线验证、正式 Tag 和 GitHub Release 是不同状态。维护者在获准发布时，只把经过检查的产品文件送入独立公开 checkout，不推送私有工作区历史。等精确公开 commit 的主线校验通过后再创建正式 Tag；Tag 工作流复核后创建 GitHub Release。外部贡献者无需作者的私有发布工具，也不要从版本号推断某个渠道已经发布。

## 高风险边界

插件安装、正式版本发布、GitHub Release、许可证变化和新平台兼容承诺属于独立决策，不因普通内容修改自动获得授权。
