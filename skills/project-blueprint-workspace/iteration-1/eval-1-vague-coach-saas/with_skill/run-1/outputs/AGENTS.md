# 编码代理项目指引

以 [ENGINEERING.md](ENGINEERING.md) 作为工作流、命令、代码规则、测试和完成定义的代理无关来源。

按任务读取：

- [PRD.md](PRD.md)：产品范围与结果
- [SPEC.md](SPEC.md) 及 `specs/`：可观察行为与追踪
- [DESIGN.md](DESIGN.md)：UI/UX 约束
- [ARCHITECTURE.md](ARCHITECTURE.md)：模块、数据与内部设计
- [SECURITY.md](SECURITY.md)：安全与隐私控制
- [DEPLOY.md](DEPLOY.md)：交付与运行

当前蓝图是草案且 implementation-ready 为 blocked。编码前暴露实质假设与冲突，不得自行决定任何 `pending` 项。仅在用户/负责人批准具体切片后，实施满足已批准 SPEC 的最小范围变更；不要绕过服务端工作区授权、预约事务或幂等要求。若请求与蓝图冲突，先提出 PRD/SPEC 变更，再运行 ENGINEERING 中适用验证。

