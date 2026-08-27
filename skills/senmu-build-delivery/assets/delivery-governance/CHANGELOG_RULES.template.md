# Changelog 规则

- 每个正式发布单元维护自己的 `VERSION` 与 `CHANGELOG.md`。
- `CHANGELOG` 只记录进入版本的变化；开发过程与未发布状态写入 `WORKLOG`。
- Git commit 历史保留逐次代码差异；不为每个机械 commit 自动复制 Work Log 或 changelog，按实质任务和版本影响留痕。
- 用户可见变化、Bug/Hotfix、部署或兼容变化必须记录；密钥、安全细节和未公开计划不得进入用户日志。
- 每条正式发布记录包含版本、日期、范围、验证、已知风险和回滚点。
