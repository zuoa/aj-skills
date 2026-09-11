---
blueprint_kind: adr
blueprint_status: proposed
owner: engineering-lead
last_reviewed: 2026-09-10
---

# ADR 0001: 以模块化单体作为服务端起点

- Status: proposed
- Date: 2026-09-10
- Decision owner: engineering lead
- Related requirements: PRD-ACTION-001, PRD-ACTION-002, PRD-SAFETY-001

## 背景与驱动因素

早期项目由一个团队交付，报名、完成记录、核验和举报需要一致授权、事务和审计。目前没有独立扩展、独立团队或独立发布证据。

## 候选

| Option | Benefits | Costs/risks | Constraint fit |
|---|---|---|---|
| 模块化单体 | 单一事务和部署路径，边界可在代码中验证 | 模块纪律不足会形成耦合 | 最符合当前证据 |
| 微服务 | 可独立部署与扩展 | 分布式事务、运维和授权复杂度 | 没有当前驱动 |

## 决定

采用模块化单体 API，模块拥有明确接口与数据访问边界；通知和媒体扫描可作为 worker 部署，但不拥有独立业务真相。

## 后果

- Positive: 身份、报名、核验和审核规则可在一个事务与审计边界内实现。
- Negative: 需要架构测试阻止跨模块直接访问。
- Follow-up: 建立模块依赖检查、幂等写入与领域事件适配器。

## 重新评估条件

独立团队需要独立发布、监管要求强制数据隔离，或实测负载无法通过单体扩展满足已批准预算。
