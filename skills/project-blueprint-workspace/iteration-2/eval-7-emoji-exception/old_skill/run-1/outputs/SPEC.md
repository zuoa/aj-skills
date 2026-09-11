---
blueprint_kind: spec-index
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
---

# 系统行为规格

## 范围与权威关系

本索引管理全局行为与追踪；详细行为位于 `specs/`。

## 术语

| Term | Meaning | Source |
|---|---|---|
| 行动 | 组织者发布的线下社区环保活动 | PRD-ACTION-001 |
| 完成记录 | 参与者提交、等待组织者核验的行动记录 | PRD-ACTION-002 |
| 核验状态 | 待核验、已通过或需补充 | PRD-ACTION-002 |

## 全局行为规则

| Rule ID | Observable rule | Source | State |
|---|---|---|---|
| GLOBAL-001 | 状态变化同时提供可见文字与辅助技术可感知的语义 | PRD-ACCESS-001 | confirmed |
| GLOBAL-002 | 重复激活不创建重复报名或完成记录 | PRD-ACTION-001; PRD-ACTION-002 | confirmed |
| GLOBAL-003 | 错误说明结果、已保存内容和下一步 | PRD-ACCESS-001 | confirmed |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Actions | [specs/actions.md](specs/actions.md) | product lead | draft |
| Accessibility | [specs/accessibility.md](specs/accessibility.md) | accessibility lead | draft |
| Safety | [specs/safety.md](specs/safety.md) | safety lead | draft |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-ACTION-001 | SPEC-ACTION-001 | DESIGN.md#信息架构与流程 | ARCHITECTURE.md#模块边界 | planned |
| PRD-ACTION-002 | SPEC-ACTION-002; SPEC-ACTION-003 | DESIGN.md#界面状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-ACCESS-001 | SPEC-ACCESS-001; SPEC-ACCESS-002 | DESIGN.md#无障碍与内容 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-SAFETY-001 | SPEC-SAFETY-001 | DESIGN.md#信息架构与流程 | ARCHITECTURE.md#模块边界 | planned |

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | PRD 用户、MVP 与用户给定设计约束 |
| implementation-ready | blocked | TBD-PRODUCT-002; TBD-SPEC-001; TBD-ARCH-001; TBD-ENGINEERING-001 | 技术基线、行为审批和命令待定 |
| production-ready | blocked | TBD-PRODUCT-001; TBD-PRODUCT-003; TBD-SECURITY-001; TBD-DEPLOY-001 | 地区、安全、数据和运行指标待定 |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 批准领域规格作为实现基线 | product/QA | 开发前 | implementation-ready | pending |
