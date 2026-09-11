# Claude Code guidance

实现前读取 [ENGINEERING.md](ENGINEERING.md)。产品与行为见 [PRD.md](PRD.md)、[SPEC.md](SPEC.md) 和 `specs/`；UI、内部边界、安全与运行分别见 [DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md)。

- 未经坐席确认绝不外发 AI 草稿；模型故障保持人工聊天。
- 强制租户隔离、幂等消息和供应商 adapter 边界。
- 冲突先报告并更新权威蓝图；仅做范围内改动，运行适用检查。
