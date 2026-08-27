# Senmu BuildOS 仓库身份与编辑边界

在修改前先判定当前根的身份：

- 存在 `.senmu-buildos/config.json`：这是内部权威库，Bug 修复、Skill 更新、测试和治理记录在此完成。
- 存在 `.senmu-public-projection.json`：这是可重建的公开投影，只允许检查和发布复核，禁止直接修改。将问题返回内部 owner 修复后重新生成投影。
- 两个标记都不存在：不要猜测当前副本是 owner；先查找工作区地图或请求用户指明权威根。

本机 Codex 刷新只消费内部库的已验证 commit。公开投影生成不等于发布；GitHub push、Tag 和 Release 需要用户单独的明确发布授权。

内部库的具体命令和门禁见 `governance/PUBLICATION.md`。
