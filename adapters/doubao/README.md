# Doubao（豆包）适配器

把 Senmu BuildOS 的七个平级 Skill 安装成豆包可加载的用户 Skill。豆包 Skill 就是 `workspace/.user_skills/<skill-name>/SKILL.md` 文件夹：**没有插件清单、没有 Marketplace、没有生命周期 Hook**，只按每个 Skill 的 `description` 路由。

## 为什么需要这个适配器

Codex 与 Claude Code 用生命周期 Hook 在会话启动时自动注入一段"治理内核"底线（例如"先看真实项目、不越权、按需加载、未验证不算完成"）。豆包没有这个 Hook 机制，所以本适配器做两件事：

1. **新增 `senmu-build-kernel` 引导内核 Skill**：把治理内核和七个专业 Skill 的路由表放在一个可命中的 Skill 里，替代 Hook 注入。
2. **提供安装脚本 `install_doubao.py`**：把七个 Skill 复制进豆包 `.user_skills`，剔除 Codex 专属的 `agents/` 元数据和缓存，并写入安装身份文件。

七个专业 Skill 的 `SKILL.md`、references、scripts、assets 与 Codex／Claude Code **共用同一份权威源**，本适配器不建立豆包专属的平行规则副本。

## 安装（两种方式任选）

### 方式 A：把仓库交给豆包，让豆包安装（推荐给不熟悉命令行的用户）

在豆包对话中粘贴下面这段话（把仓库地址换成你拿到的仓库）：

> 请把 `https://github.com/SenMuShare/senmu-buildos` 安装为豆包的用户 Skill。先读取 `adapters/doubao/README.md` 和 `adapters/doubao/install_doubao.py` 了解适配与安装逻辑，再把仓库里 `skills/` 下的七个 `senmu-build-*` Skill 以及 `adapters/doubao/kernel/` 下的 `senmu-build-kernel` 引导 Skill 复制到豆包的 `.user_skills` 目录（剔除 `agents/` 和 `__pycache__`），并写入 `.senmu-buildos-install.json` 记录版本与来源 commit。完成后报告实际安装的 Skill 列表和版本。

豆包 Agent 需要能访问本地文件系统（读取仓库、写入 `.user_skills`）和 Git／Python。这是在你自己的机器上运行的常规能力。

### 方式 B：在命令行运行安装脚本

```bash
git clone https://github.com/SenMuShare/senmu-buildos.git
cd senmu-buildos

python3 adapters/doubao/install_doubao.py --dry-run   # 预览，零写入
python3 adapters/doubao/install_doubao.py             # 安装到自动检测的豆包 .user_skills
python3 adapters/doubao/install_doubao.py --target /path/to/.user_skills   # 显式指定目标
```

脚本从仓库 `skills/` 复制七个 Skill（剔除 `agents/` 与 `__pycache__`），复制 `kernel/SKILL.md` 为 `senmu-build-kernel`，最后写入 `.senmu-buildos-install.json`（记录版本、来源 commit、安装时间与 Skill 清单）。重复运行即更新，幂等。

### 找不到 `.user_skills` 怎么办

豆包用户 Skill 的目录通常是 `<豆包工作区>/.user_skills`（与内置 Skill 同一层，内置 Skill 在 `.skills/`，用户 Skill 在 `.user_skills/`）。脚本会自动探测常见位置；如果报错找不到，用 `--target` 显式指定，或在豆包里问一句"豆包工作区的 `.user_skills` 目录在哪里"。

## 使用

- 在豆包中打开一个项目会话，用自然语言描述任务，例如"初始化这个项目的治理"、"梳理需求池并确定下一迭代"、"这个任务要分多阶段跨会话完成"。
- 需要完整治理基线时，先让 `senmu-build-kernel` 命中（如"先建立项目治理基线"），再按路由表加载对应专业 Skill。
- 七个 Skill 的正文与 Codex／Claude Code 共用，不存在豆包专属规则源。

## 边界

- **豆包无 Hook**：治理内核不能像 Codex 那样在每会话强制注入，`senmu-build-kernel` 是命中式引导，不是强制注入。这是平台能力差异，不是 Skill 缺陷；豆包路由取决于用户请求与 Skill `description` 的匹配。
- **安装只写入 `.user_skills` 目标目录**：不改豆包其他配置、不联网、不写项目文件。
- **卸载**：删除 `.user_skills` 下 `senmu-build-*` 八个目录与 `.senmu-buildos-install.json` 即可。
