# 编码代理项目指南

实现前读取 [ENGINEERING.md](ENGINEERING.md)，并按任务读取 [PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md) 和 `docs/adr/`。

暴露假设和冲突；只实现已确认规格需要的最小改动。不得让 AI 输出直接触发回滚，不得在客户端替代服务端权限、并发和审计控制。运行 ENGINEERING.md 中适用门禁；命令仍为 pending 时不得声称验证通过。
