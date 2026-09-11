---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: 2026-09-10
---

# 系统架构

## 约束与质量预算

已知约束是两个 Web 表面共享库存与预订事实，并需防止同一单册重复预订。流量、数据量、响应时间、可用性和成本目标均未提供，登记于 `TBD-ARCH-001`，不填充装饰性数字。

## 系统上下文

店员浏览器与顾客浏览器通过 HTTPS 访问同一 SaaS 应用。应用是库存、预订和店员授权的边界；关系型数据库是单册与预订的事实来源。邮件/短信、支付、外部书目和分析服务不在已确认范围。

## 容器与部署单元

| Unit | Responsibility | Interface | Data | State |
|---|---|---|---|---|
| Responsive Web | 店员桌面和顾客手机界面 | HTTPS | 不作为事实来源 | provisional |
| Modular monolith | 目录、预订、身份和审计用例 | HTTP API | 事务边界 | provisional |
| Relational database | 单册、预订、账户、审计 | DB protocol | source of truth | provisional |
| Background worker | 仅在确认通知/过期任务后引入 | internal job | 无独立所有权 | pending |

## 模块边界

| Module | Responsibility | Allowed dependencies | Related SPEC |
|---|---|---|---|
| Catalog | 书目、单册及公开投影 | shared identity/audit | SPEC-CATALOG-001, SPEC-SEARCH-001 |
| Reservations | 状态机、有效预订唯一性 | Catalog, audit | SPEC-RESERVE-001, SPEC-RESERVE-002 |
| Identity | 店员会话与角色 | audit | SPEC-ACCESS-001 |
| Audit | 追加关键管理事件 | none | SPEC-RESERVE-002 |

## 数据与一致性

- 单册和预订使用关系事务；对“每册最多一个有效预订”使用数据库可执行约束或等效串行化保护，并以并发测试验证。
- 状态变更要求预期版本，冲突返回可恢复结果而非静默覆盖。
- 公开目录只读取允许公开的投影，不暴露顾客资料、成本或审计数据。
- 具体实体字段、保留期和删除规则待领域与隐私决定。

## 技术与中间件决策

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|
| 架构形态 | 单团队/规模未知 | modular monolith / services | modular monolith | 后续拆分需清晰模块边界 | provisional | 独立团队或隔离需求出现 |
| 数据库 | 事务与并发唯一性 | relational / document | relational | 需要模式迁移 | provisional | 证据显示访问模式不适合 |
| 搜索 | 题名/作者/ISBN；规模未知 | DB indexes/full text / search service | 先用数据库能力 | 高级相关性有限 | provisional | 真实检索质量或规模不达标 |
| 缓存/消息队列 | 无测量证据 | none / managed service | 不引入 | 后续通知可能需 worker | provisional | 持久重试或热点证据出现 |

## 失败与演进

数据库不可用时公开目录说明无法取得当前库存，管理写入被禁用；不显示未经确认的缓存为最新。外部通知若后续接入，不得决定预订事务成败。组件拆分必须由独立发布、隔离或负载证据触发。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | 确认技术栈、团队能力、规模、性能、可用性和成本预算 | technical-owner | 实现前 | implementation-ready | pending |
