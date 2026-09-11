---
blueprint_kind: spec-index
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: 2026-09-10
---

# 系统行为规格索引

## 范围与权威关系

本文只负责共享术语、全局可观察规则、领域索引、追踪和就绪度。具体行为以 `specs/` 下的领域规格为准。当前规格均为草案；`provisional` 表示可讨论的工作默认，不代表用户确认。

## 术语

| 术语 | 含义 | 来源/状态 |
|---|---|---|
| 教练 | 使用网页管理端提供课程并接收预约的独立服务提供者 | 用户输入，confirmed |
| 学员 | 使用手机网页查看并提交预约的人 | 用户输入，confirmed |
| 工作区 | 隔离一位教练业务数据的逻辑边界；是否支持组织/多人待定 | 架构草案，provisional |
| 可预约时段 | 当前允许学员提交预约的时间选项；生成规则待 TBD-BOOK-001 | 产品草案，provisional |
| 有效预约 | 系统明确返回成功、且教练管理端可见的预约 | 行为草案，provisional |

## 全局行为规则

| Rule ID | 可观察规则 | 来源 | State |
|---|---|---|---|
| RULE-GLOBAL-001 | 任何失败都不得向用户显示“成功”或留下无法判断是否成立的预约结果 | PRD-BOOK-002 | provisional |
| RULE-GLOBAL-002 | 教练只能观察自己工作区的数据；未授权请求不得泄露目标是否存在之外的细节 | PRD-ACCESS-001 | provisional |
| RULE-GLOBAL-003 | 所有面向用户的时间显示必须包含足以避免歧义的日期和时间语境；时区规则待 TBD-BOOK-001 | PRD-SCHED-001 | provisional |
| RULE-GLOBAL-004 | 学员手机网页的核心预约行为不依赖原生应用安装 | PRD-BOOK-001 | confirmed |

## 领域规格

| Domain | File | Owner | State |
|---|---|---|---|
| Scheduling | [specs/scheduling.md](specs/scheduling.md) | 产品负责人（未指定） | provisional |
| Booking | [specs/booking.md](specs/booking.md) | 产品负责人（未指定） | provisional |
| Coach workspace | [specs/coach-workspace.md](specs/coach-workspace.md) | 产品/安全负责人（未指定） | provisional |

## 追踪矩阵

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|
| PRD-SCHED-001 | SPEC-SCHED-001 | [DESIGN.md#教练维护可预约时间](DESIGN.md#教练维护可预约时间) | [ARCHITECTURE.md#模块边界](ARCHITECTURE.md#模块边界) | planned |
| PRD-BOOK-001 | SPEC-BOOK-001 | [DESIGN.md#学员完成预约](DESIGN.md#学员完成预约) | [ARCHITECTURE.md#容器与可部署单元](ARCHITECTURE.md#容器与可部署单元) | planned |
| PRD-BOOK-002 | SPEC-BOOK-002 | [DESIGN.md#学员完成预约](DESIGN.md#学员完成预约) | [ARCHITECTURE.md#数据与一致性](ARCHITECTURE.md#数据与一致性) | planned |
| PRD-COACH-001 | SPEC-COACH-001 | [DESIGN.md#教练查看预约](DESIGN.md#教练查看预约) | [ARCHITECTURE.md#模块边界](ARCHITECTURE.md#模块边界) | planned |
| PRD-ACCESS-001 | SPEC-ACCESS-001 | [DESIGN.md#权限与会话状态](DESIGN.md#权限与会话状态) | [ARCHITECTURE.md#身份与授权边界](ARCHITECTURE.md#身份与授权边界) | planned |

## 就绪度台账

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PRODUCT-001, TBD-PRODUCT-002 | [PRD.md#待决定事项](PRD.md#待决定事项)；平台与角色已知，但 MVP 未确认 |
| implementation-ready | blocked | TBD-PRODUCT-003, TBD-BOOK-001, TBD-BOOK-002, TBD-IDENTITY-001, TBD-NOTIFY-001, TBD-DESIGN-001, TBD-ARCH-001, TBD-QUALITY-001, TBD-ENGINEERING-001 | 领域规格、设计和架构均为 provisional |
| production-ready | blocked | TBD-MARKET-001, TBD-SECURITY-001, TBD-DEPLOY-001, TBD-RECOVERY-001 | [SECURITY.md](SECURITY.md)；[DEPLOY.md](DEPLOY.md) |

## 待决定事项

| TBD ID | 决定 | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-QUALITY-001 | 定义真实流量、延迟、可用性与降级目标 | 产品/技术负责人（未指定） | 架构基线签署前 | implementation-ready | pending |

