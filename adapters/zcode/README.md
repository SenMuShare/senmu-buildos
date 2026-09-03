# ZCode 适配器

把 Senmu BuildOS 安装到 ZCode。ZCode 支持两种互补的安装形态，本适配器两者都覆盖：

1. **ZCode 插件**（推荐）：仓库根部的 `.zcode-plugin/plugin.json` 清单声明 `skills: ./skills/`，八个 Skill 由插件发现并加载；插件 Hook（根 `hooks/hooks.json`，`SessionStart` 事件）在每次会话启动时自动注入治理内核底线。
2. **用户级／项目级 Skill 脚本安装**：`install_zcode.py` 把八个 Skill 复制到 `~/.agents/skills/`（用户级，跨工具标准位置）或 `<仓库>/.agents/skills/`（项目级），可选附带 `senmu-build-kernel` 引导内核 Skill。

八个专业 Skill 的 `SKILL.md`、references、scripts、assets 与 Codex／Claude Code／豆包／WorkBuddy **共用同一份权威源**，本适配器不建立 ZCode 专属的平行规则副本。

## 为什么需要这个适配器

Codex 与 Claude Code 用生命周期 Hook 在会话启动时自动注入一段"治理内核"底线（例如"先看真实项目、不越权、按需加载、未验证不算完成"）。ZCode 同样支持 `SessionStart` 生命周期事件，并且会按约定路径加载插件根部 `hooks/hooks.json`，因此插件安装可以完整复用注入机制。脚本安装没有 Hook，所以本适配器提供：

1. **`.zcode-plugin/plugin.json` 插件清单**：让 ZCode 把本仓库当插件安装（技能组件 + 约定路径 Hook）。
2. **安装脚本 `install_zcode.py`**：把八个 Skill 复制进 ZCode 技能目录，剔除 Codex 专属的 `agents/` 元数据和缓存，并写入安装身份文件；`--with-kernel` 附带引导内核。
3. **`kernel/SKILL.md` 引导内核 Skill**（可选）：把治理底线和八个专业 Skill 的路由表放在一个可命中的 Skill 里，替代脚本安装缺失的 Hook 注入。

## 安装

### 方式 A：ZCode 插件市场（推荐）

1. 打开 ZCode 的 **设置 → 插件管理 → 发现** 标签页，点 **`+`** 添加市场来源：
   - GitHub 仓库：`https://github.com/SenMuShare/senmu-buildos`
2. 在列表中找到 **senmu-buildos**，点 **获取** 安装。新装插件默认启用。
3. 重新打开会话后，`SessionStart` Hook 会注入治理内核，八个 `senmu-build-*` Skill 出现在 **设置 → 技能** 与 `/` 菜单中。

网络受限导致克隆失败时，设置环境变量 `ZCODE_HTTP_PROXY=http://host:port` 后重试（ZCode 只读取该变量，裸 `http_proxy` 无效）。

### 方式 B：命令行安装脚本（纯 Skill，无 Hook）

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos

python3 adapters/zcode/install_zcode.py --dry-run              # 预览，零写入
python3 adapters/zcode/install_zcode.py                        # 用户级 ~/.agents/skills/
python3 adapters/zcode/install_zcode.py --with-kernel          # 附带引导内核 Skill
python3 adapters/zcode/install_zcode.py --scope project --workspace /path/to/repo
python3 adapters/zcode/install_zcode.py --target /path/to/skills   # 显式指定目标
```

脚本从仓库 `skills/` 复制八个 Skill（剔除 `agents/` 与 `__pycache__`），`--with-kernel` 时把 `kernel/SKILL.md` 复制为 `senmu-build-kernel`，最后写入 `.senmu-buildos-install.json`（记录版本、来源 commit、安装时间、作用域与 Skill 清单）。重复运行即更新，幂等。目标目录不存在时会自动创建。

### 两种方式怎么选

- **插件（方式 A）**：完整体验——治理内核每会话自动注入，技能随插件更新。适合把 BuildOS 作为长期工程底座。
- **脚本（方式 B）**：只装纯 Skill，不写 ZCode 客户端任何配置。`--with-kernel` 用命中式引导弥补缺失的内核注入。适合试用、受控环境或同时使用多个 Agent 工具的用户。

两种方式装同名 Skill 时，用户级／项目级技能目录优先于插件；请只选择一种，避免双份加载。

## 使用

- 在 ZCode 中打开一个项目会话，用自然语言描述任务，例如"初始化这个项目的治理"、"梳理需求池并确定下一迭代"、"这个任务要分多阶段跨会话完成"。
- 插件方式：会话启动即有治理内核；直接按任务描述路由到对应专业 Skill。
- 脚本方式（`--with-kernel`）：需要完整治理基线时，先让 `senmu-build-kernel` 命中（如"先建立项目治理基线"），再按路由表加载对应专业 Skill。
- 八个 Skill 的正文与其他平台适配共用，不存在 ZCode 专属规则源。

## 边界

- **无 `SubagentStart` 事件**：ZCode 的生命周期事件只有 `SessionStart`、`UserPromptSubmit`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PostToolUseFailure`、`Stop`。子代理底线由各专业 Skill 正文自身承载，不依赖 Hook 注入；插件安装时 ZCode 会把根 `hooks.json` 里的 `SubagentStart` 记为不支持的警告，属预期现象。
- **脚本安装不写客户端配置**：`install_zcode.py` 只写入目标技能目录，不改 `~/.zcode/cli/config.json`、不联网、不写项目文件；配置文件级 Hook 需要 `hooks.enabled: true`，本适配器不代开。
- **卸载（插件）**：在 插件管理 → 已安装 中卸载 senmu-buildos。
- **卸载（脚本）**：删除技能目录下 `senmu-build-*` 目录（`--with-kernel` 时含 `senmu-build-kernel`）与 `.senmu-buildos-install.json` 即可。
