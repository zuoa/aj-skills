---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: 2026-09-10
---

# 工程规则

- 开始实现前引用 PRD/SPEC ID，并先解决冲突或阻断性 TBD。
- 只做满足已确认行为的最小改动；不得自行加入微服务、Kafka、Elasticsearch 或 Kubernetes。
- 预约容量/并发、重复提交、对象级权限和状态转换必须自动测试。
- 不使用真实学员数据作为测试夹具，不声称未运行的检查通过。

代码仓库和技术栈尚未提供，安装、开发、测试、类型检查、lint、构建、迁移命令均 pending，不用占位命令冒充事实。

## 完成定义

需求/规格/ADR 与实现一致；适用测试有可复查证据；安全、迁移、观测和回滚影响已评审；差异只包含有意更改。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | 确认仓库、语言/框架、规范命令、质量门禁与评审责任 | technical-owner | 实现前 | implementation-ready | pending |
