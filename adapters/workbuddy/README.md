# WorkBuddy 适配器

把 Senmu BuildOS 的八个平级 Skill 安装成 WorkBuddy 可加载的 Skill。WorkBuddy Skill 就是 `<skills-root>/<skill-name>/SKILL.md` 文件夹，支持两种作用域：**用户级** `~/.workbuddy/skills/`（跨项目共享）和**项目级** `<workspace>/.workbuddy/skills/`（仅当前工作区）。WorkBuddy **没有插件清单式的生命周期 Hook**，按每个 Skill 的 `description` 路由。

## 为什么需要这个适配器

Codex 与 Claude Code 用生命周期 Hook 在会话启动时自动注入一段"治理内核"底线（例如"先看真实项目、不越权、按需加载、未验证不算完成"）。WorkBuddy 没有这个 Hook 机制，所以本适配器做两件事：

1. **新增 `senmu-build-kernel` 引导内核 Skill**：把治理内核和八个专业 Skill 的路由表放在一个可命中的 Skill 里，替代 Hook 注入。
2. **提供安装脚本 `install_workbuddy.py`**：把八个 Skill 复制进 WorkBuddy skills 目录，剔除 Codex 专属的 `agents/` 元数据和缓存，并写入安装身份文件。

八个专业 Skill 的 `SKILL.md`、references、scripts、assets 与 Codex／Claude Code／豆包**共用同一份权威源**，本适配器不建立 WorkBuddy 专属的平行规则副本。

## 安装（两种方式任选）

### 方式 A：把仓库交给 WorkBuddy，让 WorkBuddy 安装（推荐给不熟悉命令行的用户）

在 WorkBuddy 对话中粘贴下面这段话（把仓库地址换成你拿到的仓库）：

> 请把 `https://github.com/SenMuShare/senmu-buildos` 安装为 WorkBuddy 的 Skill。先读取 `adapters/workbuddy/README.md` 和 `adapters/workbuddy/install_workbuddy.py` 了解适配与安装逻辑，再运行 `python3 adapters/workbuddy/install_workbuddy.py --scope user`（安装到用户级 `~/.workbuddy/skills/`；如需仅当前项目可用，改用 `--scope project --workspace <当前工作区根目录>`）。完成后报告实际安装的 Skill 列表和版本。

WorkBuddy Agent 需要能访问本地文件系统（读取仓库、写入 skills 目录）和 Git／Python。这是在你自己的机器上运行的常规能力。

### 方式 B：在命令行运行安装脚本

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos

python3 adapters/workbuddy/install_workbuddy.py --dry-run            # 预览，零写入
python3 adapters/workbuddy/install_workbuddy.py --scope user         # 用户级 ~/.workbuddy/skills/
python3 adapters/workbuddy/install_workbuddy.py --scope project --workspace /path/to/workspace
python3 adapters/workbuddy/install_workbuddy.py --target /path/to/skills   # 显式指定目标
```

脚本从仓库 `skills/` 复制八个 Skill（剔除 `agents/` 与 `__pycache__`），复制 `kernel/SKILL.md` 为 `senmu-build-kernel`，最后写入 `.senmu-buildos-install.json`（记录版本、来源 commit、安装时间、作用域与 Skill 清单）。重复运行即更新，幂等。

### 选择用户级还是项目级

- **用户级**（默认）：所有 WorkBuddy 会话都能命中这八个 Skill，适合把 BuildOS 作为长期工程底座。
- **项目级**：只在指定工作区生效，skills 随项目目录走，适合试用或团队按项目启用。

## 使用

- 在 WorkBuddy 中打开一个项目会话，用自然语言描述任务，例如"初始化这个项目的治理"、"梳理需求池并确定下一迭代"、"这个任务要分多阶段跨会话完成"。
- 需要完整治理基线时，先让 `senmu-build-kernel` 命中（如"先建立项目治理基线"），再按路由表加载对应专业 Skill。
- 八个 Skill 的正文与 Codex／Claude Code／豆包共用，不存在 WorkBuddy 专属规则源。

## 边界

- **WorkBuddy 无插件生命周期 Hook**：治理内核不能像 Codex 那样在每会话强制注入，`senmu-build-kernel` 是命中式引导，不是强制注入。这是平台能力差异，不是 Skill 缺陷；WorkBuddy 路由取决于用户请求与 Skill `description` 的匹配。
- **安装只写入目标 skills 目录**：不改 WorkBuddy 其他配置、不联网、不写项目文件。
- **卸载**：删除 skills 目录下 `senmu-build-*` 九个目录（八个专业 Skill 加内核）与 `.senmu-buildos-install.json` 即可。
