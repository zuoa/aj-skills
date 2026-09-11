# Coding agent project guidance

先读 [ENGINEERING.md](ENGINEERING.md)。按任务读取权威文档：[PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md) 和 `docs/adr/`。

- 只实现 `confirmed` 或获 owner 接受的 `provisional` 行为；遇到相关 `pending` 决定先停止并提出蓝图更新。
- 每个数据访问显式携带 tenant 与 home region；不得跨区回退 EU 数据。
- 不在日志、测试夹具、遥测或错误中写发票正文、完整银行号、令牌、SSO 断言或密钥。
- 行为变化先更新 PRD/SPEC；完成前运行 [ENGINEERING.md](ENGINEERING.md) 登记的适用门禁。

