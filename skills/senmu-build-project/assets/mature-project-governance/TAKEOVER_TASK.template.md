# <TASK-ID>：成熟项目接管治理

> 状态：`planned`
> 权威任务 owner：`<项目已有 Issue／数据库／任务文件>`
> 控制记录：`<GOVERNANCE_CONTROL.json 或等价系统对象>`
> 最近更新：`<YYYY-MM-DD>`

## 目标、范围与完成定义

- 目标：`<用户希望治理后可观察到的结果>`
- 包含：`<发布单元／模块／主流程>`
- 非目标：`<不在本次接管中的领域>`
- 完成定义：`<Finding、复核、残余风险、交接与临时内容去留条件>`

## 授权与禁止

- 审计授权：`<允许的只读检查与临时产物>`
- 实施授权：`<pending／获批范围／declined>`
- 单独审批：`<用户行为、数据、权限、发布、删除、生产操作>`
- 禁止：`<不可越过的边界>`

## 冻结基线与恢复

| 对象 | 冻结身份 | 证据 | 恢复入口 |
| --- | --- | --- | --- |
| 项目根／仓库 |  |  |  |
| 发布／交付单元 |  |  |  |
| 运行／数据 |  |  |  |
| 已验证回滚点 |  |  |  |

## 覆盖、Finding 与用户决定

- Coverage Map／审查报告：`<原 owner 路径或对象 ID>`
- 未覆盖领域：`<not_assessed 列表>`
- Finding 登记：`<审查 owner>`

| Finding ID | 影响／严重度 | 用户决定 | 责任 owner | 整改任务／变更 | 复核条件／状态 |
| --- | --- | --- | --- | --- | --- |

## 整改波次与进度

| 波次 | 结果 | Finding | 授权前置 | 状态 | 证据／恢复点 | 下一步 |
| --- | --- | --- | --- | --- | --- | --- |

当前阶段：`<baseline／audit／decision／remediation／verification／final_review／closeout>`

## 复核、残余风险与交接

- 最终冻结对象：`<commit／version／revision／非 Git 等价身份>`
- 复核结论与证据：`<路径或对象 ID>`
- 残余风险／接受期限：`<无或列出>`
- 日常接管入口：`<README／Project Map／Issue／质量命令／发布入口>`
- 恢复时先读：`<最小文件／对象列表>`

## 临时内容去留与收口

- 工作区／中间物位置：`<项目已登记位置>`
- 用户决定：`<pending_user_decision／retain／archive／delete_authorized>`
- 正式事实回写：`<原 owner 列表>`
- 发布／生产状态：`<实际状态和 Delivery 证据／不适用>`
- 最终状态：`<completed／cancelled／archived>`
