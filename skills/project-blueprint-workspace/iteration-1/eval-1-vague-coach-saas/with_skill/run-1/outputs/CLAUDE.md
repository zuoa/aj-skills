# Claude Code 项目指引

实现前先读 [ENGINEERING.md](ENGINEERING.md)，再按任务读取权威文档：

- 产品范围：[PRD.md](PRD.md)
- 可观察行为：[SPEC.md](SPEC.md) 与其中链接的 `specs/`
- 体验约束：[DESIGN.md](DESIGN.md)
- 内部边界：[ARCHITECTURE.md](ARCHITECTURE.md)
- 安全与隐私：[SECURITY.md](SECURITY.md)
- 部署与运维：[DEPLOY.md](DEPLOY.md)

当前蓝图是草案，implementation-ready 为 blocked。不得把 pending 决策静默变成代码。若获准实现某个已确认切片，采用满足对应 SPEC 的最小变更，保持工作区授权和预约事务边界，并运行 ENGINEERING 中适用门禁。若请求改变外部行为，先提议更新 PRD/SPEC。

## Commands

- Blueprint validation: `python3 /Users/yujian/Code/py/aj-skills/skills/project-blueprint/scripts/validate_blueprint.py .`
- Install/Test/Typecheck/Build: pending，见 `TBD-ENGINEERING-001`（登记在 [ENGINEERING.md#待决定事项](ENGINEERING.md#待决定事项)）

