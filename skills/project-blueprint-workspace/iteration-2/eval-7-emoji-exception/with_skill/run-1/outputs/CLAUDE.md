# Claude Code 项目规则

实现前阅读 [ENGINEERING.md](ENGINEERING.md)，并按任务读取 [PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md) 和 `docs/adr/`。

- 先暴露假设和冲突，按已确认 SPEC 实现最小改动。
- 状态必须有文字和程序化语义，不得只用颜色、图标、位置或动画表达。
- 团队 UI 字符串默认不含 Emoji；唯一品牌例外及无障碍处理以 DESIGN.md 为准。
- 命令尚未确认，见 TBD-ENGINEERING-001；不要猜测安装、测试或构建命令。
- 请求与蓝图冲突时先提出所需 PRD/SPEC 更新，不静默改变行为。
