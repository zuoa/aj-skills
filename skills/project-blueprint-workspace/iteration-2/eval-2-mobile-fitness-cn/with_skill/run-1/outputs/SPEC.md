---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 全局规则

业务日期和提醒时区默认使用用户明确选择的时区；默认值与跨时区行为 pending。离线操作不得显示为已同步；照片和通知处理状态与打卡事实分离。

## Domain specs

| Domain | File | State |
|---|---|---|
| Authentication | [specs/auth.md](specs/auth.md) | provisional |
| Training/check-in | [specs/training.md](specs/training.md) | provisional |
| Media/notification/access | [specs/media-access.md](specs/media-access.md) | provisional |

## Traceability

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-AUTH-001 | SPEC-AUTH-001 | DESIGN.md#权限与平台行为 | ARCHITECTURE.md#模块边界 | planned |
| PRD-TRAIN-001 | SPEC-TRAIN-001 | DESIGN.md#关键界面与任务 | ARCHITECTURE.md#模块边界 | planned |
| PRD-CHECKIN-001 | SPEC-CHECKIN-001 | DESIGN.md#状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-MEDIA-001 | SPEC-MEDIA-001 | DESIGN.md#状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-NOTIFY-001 | SPEC-NOTIFY-001 | DESIGN.md#权限与平台行为 | ARCHITECTURE.md#外部依赖 | planned |
| PRD-COACH-001 | SPEC-COACH-001 | DESIGN.md#关键界面与任务 | ARCHITECTURE.md#模块边界 | planned |

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | 已知用户、平台与 MVP |
| implementation-ready | blocked | TBD-PRODUCT-001, TBD-SPEC-001, TBD-DESIGN-001, TBD-ARCH-001, TBD-ENGINEERING-001 | 业务规则/供应商/技术细节未批准 |
| production-ready | blocked | TBD-COMPLIANCE-001, TBD-SECURITY-001, TBD-DEPLOY-001 | 合规、隐私、商店、恢复和运维待核实 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 确认验证码、业务日期、编辑、照片和提醒的可观察规则 | product-owner | 实现前 | implementation-ready | pending |
