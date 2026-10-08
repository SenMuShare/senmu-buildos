# 版本与发布规则

> 文档状态：初始化草案  
> 最近校准：{{DATE}}

- 发布单元：`<待确认>`
- 发布环境与负责人：`<待确认>`
- 本地 Git 基线：`<分支、commit、Tag；本地 Git 可独立形成完整版本线>`
- Remote：`<未配置／地址与同步授权边界>`
- PR／MR、CI 与平台 Release：`<未配置／项目既有入口；不因使用 Git 自动启用>`
- 版本策略：`<SemVer、日期版本或项目规则>`
- changelog 归属：`<待确认>`
- 正式 Tag 格式：`<待确认>`；语义固定为目标发布事实验证成功后的正式版本标记
- 候选冻结身份：`<精确 commit、候选编号、制品 ID／哈希；不得用正式 Tag 代替>`
- 构建与制品入口：`<待确认或不适用>`；正式版本不自动意味着存在独立制品
- 机器可执行发布驱动：`<顶层命令／CI workflow／尚未建立>`；分散脚本和文档清单不算标准流水线
- 驱动阶段与恢复：`<plan/prepare/release/resume 或等价 jobs；幂等键、阶段收据和失败续跑入口>`
- 版本／Release Record 唯一事实：`<结构化元数据与派生文档；避免多文件手工重复更新>`
- 本次候选范围：`<精确 commit 及明确纳入的分支／需求>`
- 非阻塞并行工作：`<排除的 POC／分支／worktree、理由和后续 owner；没有则写无>`
- 共享可变资源：`<数据库／配置／端口／对象存储／部署目录及隔离或锁；没有则写无>`
- Artifact Manifest／制品库：`<待确认或不适用>`
- 发布前门禁：`<待确认>`
- 授权边界：`<谁可授权、需明确哪些范围>`
- 发布限制：`<发布单元 + 环境，可选版本线／批次；“不要发布”持久到负责人明确放行>`
- 授权会话：`<授权来源与范围、当前候选/制品、环境、重试预算；候选变化复核证据，超出授权范围或仅批准旧候选时重新确认>`
- 自然语言发布入口：项目只有一个当前发布单元、一个默认目标环境和一条标准入口时，“发布最新版本／把这批修复发布”授权执行已声明的常规版本、Tag、既有 Remote／平台、制品、部署、生产验证和记录；多单元／多环境、付费、不可逆迁移或计划外删除另行确认。
- Release Record：`<evidence/releases/ 或外部发布系统>`
- 生产事实验证：`<运行身份、健康和受影响主流程>`
- 回滚入口：`<待确认>`
- 数据／配置恢复边界：`<待确认或不适用>`
- 制品保留策略来源：`<无独立制品／用户／项目既有规则／BuildOS 默认>`；只有确认存在独立制品时才启用，默认当前已验证版本＋一个已验证可回滚版本。
- 收口资源面：`<源码发布／本机构建端／生产运行端／远程镜像或制品库／不适用项>`；只登记真实存在的资源面。
- 自动收口：存在受管制品时，复用项目已有原生入口，或校准 `operations/scripts/cleanup-release-assets.sh`；实际发布驱动应在目标验证通过后调用。治理时核对调用链及隔离成功/失败回执，不能把生成文件当作完成接线；没有独立制品时不伪造清理动作。
- 保留身份更新：每次发布由真实制品事实派生当前版、已验证回滚版和 Pin，不能沿用初始化占位值。每个配置/回执标明实际资源面和 Docker context/engine；本机结果不替代服务器/远端仓库。
- 收口结果：区分 planned、disabled、no_candidates、completed、blocked、failed；计划数量不计为实际移除数量。缺证据或错误留下原因和继续入口，不将未知当零对象。
- Git 执行面收口：本次纳入的短分支／worktree 按代码管理规范安全清理或登记保留；并行排除项不强制归零。
- 更早版本恢复等级：`<保留不可变制品／可复现重建及证据／不承诺>`。

## 发布状态

`planned → candidate → preflight_passed → authorized → deploying → deployed_unverified → released`

失败、取消和替代分别使用 `failed`、`cancelled`、`superseded`；完成回滚并验证生产事实后使用 `rolled_back`。状态不得超过实际证据。

正式发布必须让适用的 VERSION、CHANGELOG、commit、正式 Tag、公开源码、制品、线上版本和回滚点表达同一发布事实；不适用层级明确写为不适用，不得伪造。正式 Tag 只在目标发布事实验证成功后创建。
本地 Tag、远程 Tag、平台 Release 和部署是不同状态；只执行项目已配置且本次明确授权的层级，没有 Remote 不构成失败。
收到明确发布命令的当前执行者承担当次收口，责任绑定本次发布记录，不绑定固定 Agent 身份。
用户不负责决定合并、版本 commit、构建、部署和 Tag 的顺序；执行者先冻结 commit／候选／制品，验证目标发布事实后再创建正式 Tag，候选门禁失败时停下并报告。
路线图或迭代中的目标版本只是计划；完成上述发布证据后才是实际发布版本。
“准备发布”或预检通过不授权 Tag、上传、部署、切流、通知或远端清理。

正式发布授权包含本计划已经声明的项目级发布后收口；没有声明受管对象、回滚版本或清理边界时不得执行 apply。清理失败时记录为“已部署但收口未完成”，不得宣称本次发布完整结束。

## 独立资源分组调用示例

仅当项目负责人已确认各组的授权、保留集、写入排除和依赖边界独立时，才在原发布驱动中采用以下片段；它不是新的清理工具或默认全局策略。`retention-scope.txt` 示意已有项目决定，不能由执行者为了绕过失败临时改为 independent。共同依赖仍用一个完整计划，未知范围停止。先校验所有共同前提，再执行独立组；不要放宽清理助手的逐计划检查。

以下 POSIX/Python 3 示例合入原发布驱动，不新增通用清理器。路径及 verify 命令映射到现有入口；RETENTION_RECEIPT_ROOT 必须是项目内已经存在的运行回执目录，每次调用在其下独占创建一个 attempt，不覆盖历史。配置和环境变量记录既有授权，不产生授权。分组不改变制品、数据、回滚或强制验证要求；取消不是可忽略的一般错误。

<!-- independent-retention-example:start -->
```python
#!/usr/bin/env python3
"""POSIX caller example; map paths/receipts to the existing exclusive project run."""
import os
import re
import signal
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    root = Path.cwd().resolve()
    if os.name != "posix" or os.environ.get("RELEASE_CLOSEOUT_AUTHORIZED") != "1":
        return 2
    if Path(os.environ.get("RETENTION_PROJECT_ROOT", str(root))).resolve() != root:
        return 2
    # Use a pre-existing project receipt owner, never a global or disposable directory.
    receipts = Path(os.environ["RETENTION_RECEIPT_ROOT"])
    if (not receipts.is_absolute() or receipts.is_symlink() or not receipts.is_dir()
            or not receipts.resolve().is_relative_to(root) or receipts.resolve() == root):
        return 2
    os.umask(0o077)
    attempt = Path(tempfile.mkdtemp(prefix="cleanup-", dir=receipts))
    print("retention_attempt=" + str(attempt), flush=True)
    active = None
    cancelled = 0
    outcomes = {}

    def cancel(signum, frame):
        nonlocal cancelled
        cancelled = cancelled or signum
        if active is not None:
            try:
                os.killpg(active.pid, signum)
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGINT, cancel)
    signal.signal(signal.SIGTERM, cancel)

    def run(name, command):
        nonlocal active
        if cancelled:
            return 128 + cancelled
        # Exclusive creation in this attempt preserves every earlier destructive-action receipt.
        with (attempt / (name + "-cleanup.receipt")).open("xb") as out, \
                (attempt / (name + ".stderr.log")).open("xb") as error:
            active = subprocess.Popen(command, stdout=out, stderr=error, cwd=root,
                                      env={**os.environ, "RETENTION_PROJECT_ROOT": str(root)},
                                      start_new_session=True)
            if cancelled:
                cancel(cancelled, None)  # Also cover a signal delivered while Popen was starting.
            code = active.wait()  # Do not report cancellation while the helper is still running.
            active = None
        outcomes[name] = code if code >= 0 else 128 - code
        return 128 + cancelled if cancelled else outcomes[name]

    def snapshot(name, expected=None):
        # Read each known direct-child config once without following a substituted symlink.
        with os.fdopen(os.open(root / name, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError("Retention configuration must be a regular file")
            data = stream.read(65537)
        if len(data) > 65536 or b"\0" in data:
            raise ValueError("Retention configuration exceeds the bounded text format")
        values = {}
        for line in data.decode("utf-8").split("\n"):
            line = line.removesuffix("\r")
            if not line or line.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", line)
            if not match or match[1] in values:
                raise ValueError("Invalid or duplicate retention assignment")
            values[match[1]] = match[2]
        if expected is not None and (
                values.get("ARTIFACT_CLEANUP_ENABLED", "0"),
                values.get("DOCKER_IMAGE_CLEANUP_ENABLED", "0")) != expected:
            raise ValueError("Independent groups must be artifact-only and image-only")
        if values.get("ARTIFACT_CLEANUP_ENABLED", "0") == "1":
            artifact_root = (root / values.get("ARTIFACT_ROOT", "")).resolve()
            actual_attempt = attempt.resolve()
            if actual_attempt.is_relative_to(artifact_root) or artifact_root.is_relative_to(actual_attempt):
                raise ValueError("Cleanup receipts must not overlap the artifact cleanup root")
        frozen = attempt / name
        with frozen.open("xb") as stream:
            stream.write(data)
        frozen.chmod(0o400)
        return str(frozen)

    code = 2
    try:
        scope = (root / "retention-scope.txt").read_text().strip()
        if scope == "coupled":
            groups = [("coupled", snapshot("retention.env"))]
        elif scope == "independent":
            # Validate BOTH partitions before either apply. Helpers consume the exact frozen bytes.
            groups = [("local", snapshot("retention-local.env", ("1", "0"))),
                      ("image", snapshot("retention-images.env", ("0", "1")))]
        else:
            raise ValueError("Unresolved retention dependencies; no cleanup")
        code = run("verify", ["bash", "scripts/verify.sh"])
        if code == 0 and not cancelled:
            first_error = 0
            for name, config in groups:
                result = run(name, ["bash", "scripts/cleanup.sh", config, "apply"])
                first_error = first_error or result
                if cancelled or result in (130, 143):
                    first_error = 128 + cancelled if cancelled else result
                    break
            code = first_error
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        code = 2
    finally:
        with (attempt / "retention-groups.receipt").open("x") as stream:
            stream.write(" ".join(name + "_rc=" + str(outcomes.get(name, "not_called"))
                                  for name in ("local", "image", "coupled", "verify"))
                         + " cancel_signal=" + str(cancelled) + "\n")
    return 128 + cancelled if cancelled else code


if __name__ == "__main__":
    raise SystemExit(main())
```
<!-- independent-retention-example:end -->

本地配置仅启用本组制品；镜像配置仅启用本组镜像，并分别列出真实当前/回滚/固定保留身份。一个配置内同时启用两类资源时，助手仍要求其必要盘点全部成功后才删除。成功组不掩盖失败组，也不把 no_candidates 或对象数量当成磁盘释放量。空间治理还应在受影响的同一卷测量前后变化，说明并发写入、快照/共享层等归因限制；助手的 not_measured 不能改写成释放成功。

分组前校验两个配置的启用范围，并将经过检查的有限文本快照交给原清理助手；源配置变化不会改变当前调用，写入排除与授权仍由原项目保证。禁止为绕过共同失败而把决定改为 independent。脚本本身、verify 和 helper 应来自受控项目入口；此示例不为不可信代码提供沙箱。

父进程收到 INT/TERM 时向当前子进程组转发，并等待助手终止后再返回取消状态，不启动下一组。子命令不得自行脱离该组或后台化；不自动强杀、不将中断解释为删除回滚。宿主强杀、掉电、远端已提交操作或无法完成的终止仍需沿原运行记录核实，不能仅凭退出码宣布远端任务已停止或所有资源完整保留。Windows 等环境应采用宿主既有受管进程能力，不照搬 POSIX 信号实现。
