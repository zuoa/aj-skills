# Coding agent guidance

先读 [ENGINEERING.md](ENGINEERING.md)，再按任务读取 [PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md)。

- 不得绕过坐席确认发送，不得让人工聊天依赖模型。
- 所有数据访问显式校验租户；供应商只能经 adapter 调用。
- 行为冲突先更新 PRD/SPEC；实现最小改动并运行 `ENGINEERING.md` 规定的检查。
