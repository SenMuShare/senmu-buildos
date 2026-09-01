# 分支与合并规则

> 文档状态：初始化草案  
> 最近校准：{{DATE}}

- 集成基线：`<待确认>`
- 主线语义：`<release_ready／integration；未声明时禁止自动集成>`
- 直接主线写入：`禁止；所有源码修改使用任务分支`
- 正式发布基线：`<待确认>`
- AI／功能短分支命名：`<待确认>`
- 合并方式与审核门禁：`<待确认>`
- 分支保护／CI／CODEOWNERS：`<待确认或不适用>`
- 候选 revision 如何锁定：`<待确认>`
- 共享工作区与脏工作树处理：`<待确认>`
- 协作执行面：默认一个权威事实源；只读并行不切分支。所有源码修改自动使用任务短分支；为未来可新增会话或已知并行再增加独立 worktree。只有项目／Harness 保证整个窗口独占写入时才复用当前目录，不能因此直接写主线。
- Remote／PR／MR／CI：`<未配置／已配置及授权边界；没有 Remote 不构成缺陷>`
- 合并策略：`<squash／rebase／merge commit；pull --ff-only 不等于合并策略>`
- 提交交接：开发执行者完成验证和本地 commit；推送与 PR／MR 仅在 Remote 存在且授权覆盖时执行。
- Change Unit：`<任务／需求 ID、目标版本线、基线、分支／worktree、sealed commit、范围、测试、依赖／冲突、状态>`；已有任务 owner 时只写回该 owner。
- 待接收视图：由 `sealed` 且尚无最终 disposition 的 Change Unit 派生，不建立第二套任务台账。
- 分支拓扑：任务分支默认从上述集成基线建立并回到该线；禁止隐式任务链。真实依赖堆叠登记 `<child unit -> sealed parent unit -> integration order>`。
- 临时职责：实现者封口 Change Unit；收到合并／发布命令的当前 Agent 负责接收矩阵、审查、集成和候选收口，不登记固定 Team Leader。
- worktree 仅作为临时源码执行面；正式状态、台账、交付和发布入口归属项目登记的各自 owner。POC 使用独立
  `POC_ROOT`，不得因状态归属要求写入产品 `main` 或发布工作树。
- 跨 Agent／会话续作传递稳定 Change Unit ID，并用 `manage_change_unit.py resume` 回到原分支和 worktree。

## 发布收口控制

- 每次发布从 `RELEASE_CONTROL.template.json` 建立一份控制单；项目已有等价机器可读 owner 时复用，不双写。
- 控制单按顺序登记需求、Change Unit 接收矩阵、候选、授权、发布验证和 Git 执行面清理；每一门附证据，未完成时保留 checkpoint 与下一动作。
- 只有候选可达变化、本次承诺缺口或共享资源冲突阻断；历史、POC、未完成、来源不明和无关分支不得机械全合并。
- 未提交源码只能是 `in_progress`，不能由收口者猜入候选。
- 每个纳入单元的短分支／worktree 最终必须 `removed`，或以 owner 和退出条件明确 `retained`。
- 发布身份：`reviewed_commit = tested_commit = release_source_head = tag_commit = artifact_source_commit`；不适用阶段留空，已有阶段不得不一致。

## 代码变更审查门禁

- 审查对象：`<base_commit..head_commit>`
- 审查记录 owner：`<PR／MR／审批系统／change-review.json>`
- 审查身份：`<G2-G3 peer／人类／分离审查 Agent；G4 independent>`
- 变更清点：`<文件、函数／方法／顶层单元、被修改注释、排除理由>`
- 必需检查：`<快速／完整质量、测试、构建、架构／安全检查>`
- 批准失效：当前 `head_commit` 与 `reviewed_head` 不一致时必须复核，不允许沿用过期批准。
- 合并条件：变更文件／单元／注释 pending 和 blocked 为零，必需检查通过，开放 Finding 为零，P0／P1 不得接受风险。
- 本地候选：没有 Remote 时仍由项目唯一 merge／promote 入口执行等价校验，不把未配置平台当豁免。

## Worktree 授权与位置

- 只读任务不得创建分支或 worktree；写入任务始终创建短分支，未知并行默认增加 worktree，不等待用户预告并发数量。
- worktree 依据：`<Codex 写入默认 parallel-capable／必须同时运行比较／独占写入保证／无；实现授权已覆盖本地可逆隔离，不要求用户选择 Git 术语>`
- 创建前成本：`<源码／依赖／缓存／submodule／数据库／模型／媒体／非 Git 资产；不适用则写无>`
- 受管 worktree 容器：`<按权威项目根、Git 仓库与现有约定确认；可为项目内 .worktrees/、仓库相邻目录或其他登记位置；不适用则写无>`
- 位置判定：不得从当前工作目录猜测；Codex／Agent 管理目录只有在其本身是已确认项目边界或受管容器时才可使用，系统临时目录、下载目录、其他项目和未登记个人路径禁用。
- worktree 登记字段：路径、分支、用途、集成目标、正式入口、保留条件、清理条件。
- 合并后收口：从权威主目录复验分支、HEAD、版本、质量命令和交付入口，再移除无独有事实的 worktree。
- 完成状态：临时分支／worktree 必须“已安全清理”或“登记保留理由、owner 与退出条件”，不得无主残留。

## 并行版本线（按需）

| 角色 | 分支 | 版本 | 基于 | 最终去向 |
| --- | --- | --- | --- | --- |
| 当前正式主线 | `<项目登记的 current_line>` | `<当前版本／渠道>` | `<commit/tag>` | 持续维护至主线切换 |
| 继任版本线 | `<项目登记的 successor_line>` | `<候选版本／渠道>` | `<commit/tag>` | `<目标主线，必须晋升>` |
| 当前线 Hotfix | `<项目命名>` | `<patch／build／渠道修订>` | `<current_line>` | `<current_line，并按适用性前向同步>` |
| 继任线任务分支 | `<项目命名>` | `<dev／candidate>` | `<successor_line>` | `<successor_line>` |

- 继任版本是否确定替换主线：`<是／否；若是，分支完成不等于项目完成>`
- 版本标识方案：`<SemVer／CalVer／构建号／渠道／无数字；不得从示例数字推断版本角色>`
- Hotfix 前向传播检查点：`<例如功能切片完成／集成测试前／候选冻结前；不得机械固定频率>`
- 立即传播条件：`<安全／权限／支付／数据／共享契约／阻塞继任线；按项目校准>`
- 传播通知边界：通知默认登记事实，不自动中断接收方任务、扩大版本范围或授权发布。
- 主线晋升条件：`<需求、迁移、兼容、测试、部署、回滚>`
- 预计切换点：`<待确认>`
- 失败恢复方式：`<待确认>`
- 分支与临时 worktree 清理条件：`<待确认>`
- 写入任务按 `目标版本线 + 发布单元 + Change Unit` 动态分组，每组默认独立短分支和 worktree；多个维护线修复组可与继任大版本组同时存在。项目禁止、基线不清或共享状态无法隔离时改为串行；仅有覆盖整个窗口的独占写入保证时使用当前目录快速通道。
- 继任线晋升前清零所有仍适用的当前线 Hotfix；晋升验证后旧线转为 EOL／只读历史并保留 Tag、必要分支和回滚证据，不删除历史或把新主线反向合回旧线。
- 共享或受保护分支禁止强推；私有短分支历史重写也只在项目允许、无人依赖且明确获准时使用 `--force-with-lease`。

### Hotfix 前向传播记录

每个源修复只维护一行；补充 commit 或纠正更新原行，不重复生成命令式合并任务。

| 源 commit／PR／tag | 目标线 | 适用性 | 状态 | 时机／截止条件 | 集成方式 | 验证与回执 |
| --- | --- | --- | --- | --- | --- | --- |
| `<稳定源身份；紧急临时源标 provisional>` | `<next 分支>` | `<unassessed／applicable／not_applicable／superseded>` | `<observed／queued／integrating／verified>` | `<immediate／checkpoint／release_gate>` | `<merge／cherry-pick／等价重做／不适用>` | `<测试、集成 commit、理由或风险>` |
