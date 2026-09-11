# Claude Code 项目指南

先读取 [ENGINEERING.md](ENGINEERING.md)。产品、行为、体验、内部边界、安全和运行事实分别由 [PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md) 和 [DEPLOY.md](DEPLOY.md) 管理。

实现前说明重大假设和冲突。选择满足已确认 SPEC 的最小方案；禁止由模型输出直接授权或执行回滚。命令在 `TBD-ENGINEERING-001` 关闭前保持 pending，不虚构测试结果。
