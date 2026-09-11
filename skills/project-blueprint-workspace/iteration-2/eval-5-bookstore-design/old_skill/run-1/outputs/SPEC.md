---
blueprint_kind: spec-index
blueprint_status: draft
owner: bookstore-owner
last_reviewed: 2026-09-10
---

# 系统行为规格

## 范围与术语

本文件只管理共享行为、领域索引、追踪和就绪度。单册指可独立定价、描述品相和变更状态的一件实物；有效预订指尚未拒绝、取消、过期或完成的预订。

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | State |
|---|---|---|---|
| RULE-001 | 所有状态变更返回明确结果；失败不伪装成成功 | PRD-RESERVE-002 | provisional |
| RULE-002 | 日期、时间、币种和预订到期规则由地区配置决定 | TBD-PRODUCT-001 | pending |
| RULE-003 | 同一单册至多有一个有效预订 | PRD-RESERVE-001 | provisional |

## Domain specs

| Domain | File | Owner | State |
|---|---|---|---|
| Catalog and search | [specs/catalog.md](specs/catalog.md) | product/engineering | provisional |
| Reservations and access | [specs/reservations.md](specs/reservations.md) | product/engineering | provisional |

## Traceability

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-CATALOG-001 | SPEC-CATALOG-001 | DESIGN.md#店员桌面-web | ARCHITECTURE.md#模块边界 | planned |
| PRD-SEARCH-001 | SPEC-SEARCH-001 | DESIGN.md#顾客手机网页 | ARCHITECTURE.md#模块边界 | planned |
| PRD-RESERVE-001 | SPEC-RESERVE-001 | DESIGN.md#顾客手机网页 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-RESERVE-002 | SPEC-RESERVE-002 | DESIGN.md#店员桌面-web | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-ACCESS-001 | SPEC-ACCESS-001 | DESIGN.md#关键界面与主要任务 | ARCHITECTURE.md#系统上下文 | planned |

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | PRD 用户、平台和 MVP 范围足以开始线框设计 |
| implementation-ready | blocked | TBD-PRODUCT-001, TBD-DESIGN-001, TBD-ARCH-001, TBD-ENGINEERING-001 | 行为、视觉、技术与测试默认值尚未批准 |
| production-ready | blocked | TBD-METRIC-001, TBD-SECURITY-001, TBD-DEPLOY-001 | 隐私、运维与恢复责任未知 |

## Open decisions

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 以真实店铺样本确认状态词、过期与取消行为 | bookstore-owner | 实现前 | implementation-ready | pending |
