---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与术语

详细行为在 `specs/`。时段指带开始/结束、容量和发布状态的可预约安排；有效预约的状态集合及取消规则待确认。

## Global behavior rules

| Rule | Observable behavior | Source | State |
|---|---|---|---|
| RULE-001 | 日期时间显示时区，具体时区规则待定 | TBD-PRODUCT-001 | pending |
| RULE-002 | 写入失败不显示成功；重复提交不产生重复预约 | PRD-BOOKING-001 | provisional |

## Domain specs

| Domain | File | Owner | State |
|---|---|---|---|
| Scheduling and booking | [specs/booking.md](specs/booking.md) | product/engineering | provisional |

## Traceability

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-SCHEDULE-001 | SPEC-SCHEDULE-001 | DESIGN.md#关键界面与任务 | ARCHITECTURE.md#模块边界 | planned |
| PRD-BOOKING-001 | SPEC-BOOKING-001 | DESIGN.md#关键界面与任务 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-BOOKING-002 | SPEC-BOOKING-002 | DESIGN.md#状态与恢复 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-ACCESS-001 | SPEC-ACCESS-001 | DESIGN.md#关键界面与任务 | ARCHITECTURE.md#系统上下文 | planned |

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | 用户、平台与暂定 MVP 足以开始低保真设计 |
| implementation-ready | blocked | TBD-PRODUCT-001, TBD-SPEC-001, TBD-DESIGN-001, TBD-ARCH-001, TBD-ENGINEERING-001 | 业务规则、技术与测试未批准 |
| production-ready | blocked | TBD-METRIC-001, TBD-SECURITY-001, TBD-DEPLOY-001 | 指标、隐私、运维与恢复责任未知 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 用真实教练流程确认时段、容量、取消和通知状态 | product-owner | 实现前 | implementation-ready | pending |
