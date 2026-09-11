---
blueprint_kind: spec-index
blueprint_status: draft
owner: product-lead
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与权威关系

本文件管理共享规则、领域索引、追踪和就绪度；具体可观察行为位于 `specs/`。视觉表现由 `DESIGN.md` 管理，内部实现由 `ARCHITECTURE.md` 管理。

## 术语

| 术语 | 含义 | 来源 |
|---|---|---|
| 行动 | 由经授权组织者发布的线下社区环保活动 | PRD-ACTION-001 |
| 完成记录 | 参与者在行动后提交、供组织者核验的记录 | PRD-ACTION-002 |
| 状态文本 | 不依赖颜色、图形或位置即可表达的可见文字 | PRD-ACCESS-001 |

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | State |
|---|---|---|---|
| GLOBAL-001 | 保存、提交、失败和状态变化必须提供可见文字；动态结果由辅助技术可感知 | PRD-ACCESS-001 | confirmed |
| GLOBAL-002 | 同一操作不得因重复激活而创建重复报名或完成记录 | PRD-ACTION-001; PRD-ACTION-002 | confirmed |
| GLOBAL-003 | 失败消息说明发生了什么、已保存什么和可执行的下一步 | PRD-ACCESS-001 | confirmed |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Actions | [specs/actions.md](specs/actions.md) | product lead | draft |
| Accessibility | [specs/accessibility.md](specs/accessibility.md) | design and QA leads | draft |
| Safety | [specs/safety.md](specs/safety.md) | trust and safety lead | draft |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-ACTION-001 | SPEC-ACTION-001 | DESIGN.md#信息架构与关键流程 | ARCHITECTURE.md#模块边界 | planned |
| PRD-ACTION-002 | SPEC-ACTION-002; SPEC-ACTION-003 | DESIGN.md#状态矩阵 | ARCHITECTURE.md#数据与一致性 | planned |
| PRD-ACCESS-001 | SPEC-ACCESS-001; SPEC-ACCESS-002 | DESIGN.md#无障碍与内容 | ARCHITECTURE.md#接口与集成 | planned |
| PRD-SAFETY-001 | SPEC-SAFETY-001 | DESIGN.md#信息架构与关键流程 | ARCHITECTURE.md#模块边界 | planned |

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready | none | PRD.md 用户、任务与 MVP；DESIGN.md 已确认品牌和无障碍约束 |
| implementation-ready | blocked | TBD-PRODUCT-002; TBD-ENGINEERING-001 | 平台与仓库命令尚未确认 |
| production-ready | blocked | TBD-PRODUCT-001; TBD-PRODUCT-003; TBD-PRODUCT-004; TBD-SECURITY-001; TBD-DEPLOY-001 | 青少年安全、隐私、运营与恢复要求待确认 |

## Open decisions

| TBD ID | 决策 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | 由产品与 QA 批准领域规格作为实现基线 | product and QA leads | 首个开发任务前 | implementation-ready | pending |
