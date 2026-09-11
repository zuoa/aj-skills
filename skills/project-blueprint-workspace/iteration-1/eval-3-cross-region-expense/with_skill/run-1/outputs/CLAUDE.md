# Claude Code project guidance

实现前读取 [ENGINEERING.md](ENGINEERING.md)，再按任务读取：[PRD.md](PRD.md)、[SPEC.md](SPEC.md) 与 `specs/`、[DESIGN.md](DESIGN.md)、[ARCHITECTURE.md](ARCHITECTURE.md)、[SECURITY.md](SECURITY.md)、[DEPLOY.md](DEPLOY.md) 和 `docs/adr/`。

## Behavior

- 暴露假设、歧义、冲突与取舍；不得把 pending 当作事实。
- 采用满足已确认 SPEC 的最小变更，不做无关重构。
- 所有数据路径强制 tenant/home-region 边界；EU 数据不得故障转移到非 EU。
- SSO、支付、上传、特权访问和迁移改动必须运行对应负向/恢复测试。
- 请求与蓝图冲突时，先提出 PRD/SPEC 更新。

## Commands

技术栈尚未确认。安装、开发、测试、类型检查和构建命令由 `TBD-ENGINEERING-001` 决定后在 [ENGINEERING.md](ENGINEERING.md) 维护；不要自行发明替代命令。

