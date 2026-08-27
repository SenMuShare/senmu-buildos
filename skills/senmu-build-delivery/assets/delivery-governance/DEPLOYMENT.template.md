# 部署与运行

> 文档状态：初始化草案  
> 最近校准：{{DATE}}

- 本地启动：`<待确认>`
- 环境清单（local/test/staging/production）：`<待确认>`
- 配置、密钥与证书 owner：`<待确认>`
- 依赖服务与数据 owner：`<待确认>`
- 构建／部署入口：`<待确认>`
- 目标平台／运行时：`<待确认>`
- 日常部署、首次初始化与灾备入口：`<分别列出>`
- health／readiness：`<待确认>`
- 运行版本／镜像 digest／静态 revision：`<待确认>`
- 用户可见主流程验证：`<待确认>`
- 数据备份／迁移：`<待确认>`
- 回滚目标、触发条件与执行入口：`<待确认>`
- 回滚后的生产验证：`<待确认>`
- 日志、制品和缓存保留：按发布计划中的项目策略执行；未声明时默认保留当前已验证版本和一个已验证可回滚版本，特例、Pin 和退出条件写入发布计划。
- 收口资源面：本机构建端、生产运行端、远程镜像／制品库分别登记入口和不适用项；主机收口不能代替 registry 生命周期。
- 发布收口配置：`operations/release-retention.env`；初始化后校准受管制品目录、镜像仓库和当前／上一版本，不在其中填写生产秘密。
- 发布收口脚本：`operations/scripts/cleanup-release-assets.sh`。先执行 `dry-run`；只有目标版本、健康和受影响主流程通过后，正式部署入口才能以 `RELEASE_CLOSEOUT_AUTHORIZED=1 ... apply` 调用，并在运行端成功后执行构建端收口。
- Git 收口：本次纳入的短分支和临时 worktree 按 `delivery/BRANCHING.md` 或项目等价 owner 处理；清理脚本不删除 Git 对象，并行排除项保持原状。
- 收口契约测试：`operations/scripts/test-release-retention.sh`。
- 密钥只通过受控环境注入，不写入本文档或 Git。
- 部署命令退出 0 不等于发布完成；实际生产身份和受影响主流程通过后才能登记 `released`。
- 清理只允许作用于配置中声明的项目制品根和受管镜像仓库；不得使用全局 `docker system prune`、`docker image prune`、Builder Cache 清理或 Volume 删除代替项目级收口。
