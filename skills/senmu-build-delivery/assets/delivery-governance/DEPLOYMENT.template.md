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

## 对外服务安全基线

<!-- public-security-baseline:v1 -->

先确认是否对外可达、入口和实际风险；离线或仅分发源码的项目注明不适用及原因。下表是待校准的导航和证据位置，不是已部署的防护。使用现有平台／框架控制，不另建一套安全台账；初次公网暴露前，适用的关键缺口必须回到技术或运维 owner 处理。

| 控制 ID | 需要确认的边界 | 配置／验证入口 | 当前结果 |
| --- | --- | --- | --- |
| network | 真实公网入口、监听端口、云与主机规则；数据库和管理端口的访问范围 | `<待确认>` | unverified |
| edge-origin | 上游 DDoS／WAF／CDN 能力及源站绕过限制，正常访问与直接源站拒绝 | `<待确认>` | unverified |
| tls-proxy | TLS、证书续期和可信代理头；不能伪造来源绕过限制 | `<待确认>` | unverified |
| application | 后端身份与租户授权、上传和远程 URL 的安全边界 | `<现有技术规格和负向测试>` | unverified |
| resource-cost | 用户／租户请求、任务大小、并发、队列、超时和第三方费用限制 | `<待确认>` | unverified |
| host-container | 运行用户、补丁、挂载、能力和管理接口最小暴露 | `<待确认>` | unverified |
| secrets-supply | 密钥注入／轮换、制品来源及实际依赖／秘密／配置扫描范围 | `<待确认>` | unverified |
| detection | 错误、饱和、拒绝和费用异常，告警接收人与处置入口 | `<待确认>` | unverified |
| recovery | 备份访问与隔离恢复验证；镜像回滚不能替代数据备份 | `<待确认>` | unverified |

结果使用 planned、configured、verified、failed、unverified 或有依据的 not_applicable，附目标、时间和证据。配置存在、扫描通过和系统安全是不同结论；相同配置的有效证据可复用，暴露和运行事实改变时补验。公网容量防护需要上游能力，业务限流不能独自抵御所有 DDoS。未经授权不做压力攻击、生产网络修改或付费开通。
