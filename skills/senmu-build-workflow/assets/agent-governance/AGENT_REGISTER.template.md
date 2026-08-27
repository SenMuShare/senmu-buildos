# {{PROJECT_NAME}} Agent 登记表

> Professional Name：Agent Register
> 文档状态：初始化草案
> 最近校准：{{DATE}}

本表是项目自有 Agent 的唯一索引，只登记当前定义、版本、状态和运行入口，不复制系统提示词正文。根目录 `AGENTS.md` 是 Codex 项目工作入口，Skill 内 `agents/openai.yaml` 是展示元数据，二者都不得登记为项目业务 Agent。

## 目录与命名契约

- Agent 根目录：`agents/`
- 单个 Agent：`agents/{agent-key}/AGENT.md`
- `agent-key` 使用稳定的小写 kebab-case；重命名展示名称不改变 Key。
- `AGENT.md` 是角色、Prompt、输入输出、工具、流程、约束和质量门禁的唯一契约。
- 历史版本默认由 Git commit／tag 与运行记录追溯；只有确实并行运行多个版本时才建立项目明确登记的版本化运行制品。

## Agent 登记

| Agent Key | Agent 名称 | Agent Version | 状态 | 定义路径 | Owner | 关联 Workflow／Harness |
| --- | --- | --- | --- | --- | --- | --- |

允许状态：`draft`、`active`、`deprecated`、`retired`。正式运行记录必须关联 Agent Key、Agent Version、定义 commit／制品身份和实际运行入口。

## 变更与退役规则

- 改变角色权限、输入输出契约、工具授权、关键决策或兼容性时，更新 Agent Version，并同步登记表和受影响 Workflow／Harness。
- 只修改单次任务对象、游标、step、attempt 或 checkpoint 时，不修改 Agent 定义；这些事实进入任务包或运行状态 owner。
- `deprecated` 表示仍可兼容运行但已有替代；`retired` 表示不得再启动新运行。替代关系写入对应 Agent 定义和项目地图。
